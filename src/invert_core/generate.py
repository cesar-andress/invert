from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from invert.generate import extract_code
from invert.models import create_client
from invert.schemas import load_yaml

from invert_core.pilot_config import CoreV2GenerationItem, CoreV2PilotConfig, plan_core_v2_generations
from invert_core.prompts import build_generation_prompt, build_stub_code
from invert_core.stripping import StripLevel, strip_code


def _print_dry_run(pilot: CoreV2PilotConfig, items: list[CoreV2GenerationItem]) -> None:
    tasks = sorted({item.task.task_id for item in items})
    models = sorted({item.model for item in items})
    methods = sorted({item.method for item in items})
    reps = max((item.rep for item in items), default=0)
    data_root = pilot.data_root
    results_dir = pilot.results_dir

    print("Dry run — no API calls will be made.")
    print(f"Run: {pilot.run_name}")
    print(f"Family/dimension: {pilot.family}/{pilot.dimension}")
    print(f"Selected tasks ({len(tasks)}): {', '.join(tasks)}")
    print(f"Methods ({len(methods)}): {', '.join(methods)}")
    print(f"Models ({len(models)}): {', '.join(models)}")
    print(f"Repetitions: {reps}")
    print(f"Strip levels: {', '.join(pilot.strip_levels)}")
    print(f"Total expected generations: {len(items)}")
    print(f"Results directory: {results_dir}")
    print("Output paths (raw + code + stripped per level):")
    for item in items:
        print(f"  {item.raw_path(data_root)}")
        print(f"  {item.code_path(data_root)}")
        for level in pilot.strip_levels:
            print(f"  {item.stripped_path(data_root, level)}")


def _write_stripped_variants(
    pilot: CoreV2PilotConfig,
    item: CoreV2GenerationItem,
    code: str,
) -> None:
    data_root = pilot.data_root
    for level_name in pilot.strip_levels:
        out_path = item.stripped_path(data_root, level_name)
        if level_name == "raw":
            stripped = code
        else:
            stripped = strip_code(code, StripLevel(level_name))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(stripped, encoding="utf-8")


def _write_run_metadata(pilot: CoreV2PilotConfig) -> Path:
    metadata = {
        "run_name": pilot.run_name,
        "family": pilot.family,
        "dimension": pilot.dimension,
        "tasks": pilot.task_ids,
        "methods": pilot.methods,
        "models": pilot.models,
        "repetitions": pilot.repetitions,
        "strip_levels": pilot.strip_levels,
        "expected_generations": pilot.expected_generations(),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "config_file": str(pilot.config_path),
    }
    pilot.results_dir.mkdir(parents=True, exist_ok=True)
    out_path = pilot.results_dir / "metadata.json"
    out_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return out_path


def run_core_v2_generation(
    pilot: CoreV2PilotConfig,
    *,
    dry_run: bool = False,
) -> None:
    tasks = pilot.load_tasks()
    items = plan_core_v2_generations(pilot, tasks)

    if dry_run:
        _print_dry_run(pilot, items)
        return

    _write_run_metadata(pilot)
    models_cfg = load_yaml(pilot.models_config)["providers"]
    clients: dict[str, object] = {}
    data_root = pilot.data_root

    for item in items:
        model_name = item.model
        if model_name not in models_cfg:
            raise ValueError(f"Model {model_name} not found in {pilot.models_config}")
        if model_name not in clients:
            clients[model_name] = create_client(model_name, models_cfg[model_name])
        client = clients[model_name]

        raw_path = item.raw_path(data_root)
        code_path = item.code_path(data_root)
        if raw_path.exists() and code_path.exists() and not pilot.overwrite:
            print(f"SKIP existing: {code_path}")
            continue

        prompt = build_generation_prompt(item.task, item.method, language=pilot.language)
        if model_name == "local_stub":
            response = build_stub_code(item.task, item.method)
            code = response
        else:
            response = client.generate(prompt)
            code = extract_code(response)

        raw_path.parent.mkdir(parents=True, exist_ok=True)
        code_path.parent.mkdir(parents=True, exist_ok=True)

        record = {
            "run_name": pilot.run_name,
            "model": model_name,
            "task_id": item.task.task_id,
            "method": item.method,
            "rep": item.rep,
            "prompt": prompt,
            "response": response,
            "code": code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "parameters": {
                "temperature": models_cfg[model_name].get("temperature", 0),
                "family": pilot.family,
                "dimension": pilot.dimension,
            },
        }

        raw_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        code_path.write_text(code + ("\n" if not code.endswith("\n") else ""), encoding="utf-8")
        _write_stripped_variants(pilot, item, code)
        print(f"Wrote {code_path}")
