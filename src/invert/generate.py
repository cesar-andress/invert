from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from invert.config import GenerationItem, PilotConfig, plan_generations, write_run_metadata
from invert.models import create_client
from invert.prompts import build_generation_prompt
from invert.schemas import Task, load_tasks, load_yaml


def extract_code(response: str) -> str:
    fence_pattern = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
    match = fence_pattern.search(response)
    if match:
        return match.group(1).strip()
    return response.strip()


def _intent_tags(dimension_values: dict[str, str]) -> str:
    return "\n".join(f"# invert:{dim}={val}" for dim, val in sorted(dimension_values.items()))


def _print_dry_run(items: list[GenerationItem], data_dir: Path) -> None:
    tasks = sorted({item.task.task_id for item in items})
    models = sorted({item.model for item in items})
    reps = max((item.rep for item in items), default=0)
    print("Dry run — no API calls will be made.")
    print(f"Selected tasks ({len(tasks)}): {', '.join(tasks)}")
    print(f"Selected generator models ({len(models)}): {', '.join(models)}")
    print(f"Repetitions: {reps}")
    print(f"Total expected generations: {len(items)}")
    print("Output paths:")
    for item in items:
        raw_path, code_path = item.paths(data_dir)
        print(f"  {raw_path}")
        print(f"  {code_path}")


def run_generation(
    models: list[str],
    tasks_path: Path,
    repetitions: int,
    data_dir: Path,
    models_config_path: Path,
    *,
    task_ids: list[str] | None = None,
    dry_run: bool = False,
    overwrite: bool = False,
    max_generations: int | None = None,
    pilot: PilotConfig | None = None,
    project_root: Path | None = None,
) -> None:
    all_tasks = load_tasks(tasks_path)
    if task_ids:
        by_id = {t.task_id: t for t in all_tasks}
        missing = [tid for tid in task_ids if tid not in by_id]
        if missing:
            raise ValueError(f"Unknown task IDs: {missing}")
        tasks = [by_id[tid] for tid in task_ids]
    else:
        tasks = all_tasks

    items = plan_generations(tasks, models, repetitions)

    if max_generations is not None and len(items) > max_generations:
        raise ValueError(
            f"Planned {len(items)} generations exceeds max_generations={max_generations}"
        )

    if dry_run:
        _print_dry_run(items, data_dir)
        return

    if pilot is not None and project_root is not None:
        write_run_metadata(pilot, models_config_path, project_root)

    models_cfg = load_yaml(models_config_path)["providers"]
    clients: dict[str, object] = {}

    for item in items:
        model_name = item.model
        if model_name not in models_cfg:
            raise ValueError(f"Model {model_name} not found in config")
        if model_name not in clients:
            clients[model_name] = create_client(model_name, models_cfg[model_name])
        client = clients[model_name]

        raw_path, code_path = item.paths(data_dir)
        if raw_path.exists() and not overwrite:
            print(f"SKIP existing: {raw_path}")
        if code_path.exists() and not overwrite:
            print(f"SKIP existing: {code_path}")
        if raw_path.exists() and code_path.exists() and not overwrite:
            continue

        dimension_values = item.task.default_dimension_values()
        dimension_values[item.dimension] = item.value
        prompt = build_generation_prompt(item.task, dimension_values)
        response = client.generate(prompt)
        code = extract_code(response)

        if model_name == "local_stub" and "# invert:" not in code:
            code = _intent_tags(dimension_values) + "\n\n" + code

        raw_path.parent.mkdir(parents=True, exist_ok=True)
        code_path.parent.mkdir(parents=True, exist_ok=True)

        record = {
            "model": model_name,
            "task_id": item.task.task_id,
            "dimension": item.dimension,
            "value": item.value,
            "rep": item.rep,
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "parameters": {
                "temperature": models_cfg[model_name].get("temperature", 0),
            },
        }

        if not raw_path.exists() or overwrite:
            with open(raw_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)
        if not code_path.exists() or overwrite:
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)


def find_code_files(
    data_dir: Path,
    models: list[str] | None = None,
    task_ids: list[str] | None = None,
) -> list[Path]:
    code_root = data_dir / "code"
    if not code_root.exists():
        return []
    files = sorted(code_root.rglob("rep_*.py"))
    if models:
        files = [f for f in files if f.parts[f.parts.index("code") + 1] in models]
    if task_ids:
        files = [f for f in files if f.parts[f.parts.index("code") + 2] in task_ids]
    return files
