from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from invert.generate import extract_code
from invert.schemas import load_yaml
from invert_core.bfs_dfs_prompts import build_bfs_dfs_generation_prompt, build_bfs_dfs_stub_code
from invert_core.bfs_dfs_tasks import filter_bfs_dfs_tasks, load_bfs_dfs_tasks
from invert_core.deterministic_randomized_tasks import (
    filter_deterministic_randomized_tasks,
    load_deterministic_randomized_tasks,
)
from invert_core.eager_lazy_prompts import (
    build_eager_lazy_generation_prompt,
    build_eager_lazy_stub_code,
)
from invert_core.eager_lazy_tasks import filter_eager_lazy_tasks, load_eager_lazy_tasks
from invert_core.models import OllamaClient, parse_ollama_model, sanitize_model_for_storage
from invert_core.randomized_prompts import (
    build_deterministic_randomized_generation_prompt,
    build_deterministic_randomized_stub_code,
)

from invert_discovery.temperature_diversity.protocol import PILOT_PROTOCOL, PilotProtocol


def _artifact_paths(
    protocol: PilotProtocol,
    *,
    project_root: Path,
    model: str,
    class_id: str,
    task_id: str,
    pole: str,
    temperature: float,
    rep: int,
) -> tuple[Path, Path]:
    root = protocol.data_root(project_root)
    storage = sanitize_model_for_storage(model)
    stem = f"T{temperature:g}_rep_{rep}"
    base = root / storage / class_id / task_id / pole
    return base / f"{stem}.json", base / f"{stem}.py"


def _build_prompt(
    protocol: PilotProtocol,
    project_root: Path,
    class_id: str,
    task: Any,
    pole: str,
) -> str:
    spec = protocol.classes[class_id]
    dimension = spec["dimension"]
    if dimension == "eager_vs_lazy":
        return build_eager_lazy_generation_prompt(task, pole, language="python")
    if dimension == "bfs_vs_dfs":
        return build_bfs_dfs_generation_prompt(task, pole, language="python")
    if dimension == "deterministic_vs_randomized":
        return build_deterministic_randomized_generation_prompt(task, pole, language="python")
    raise ValueError(f"unsupported dimension {dimension}")


def _load_tasks(protocol: PilotProtocol, project_root: Path, class_id: str) -> list[Any]:
    spec = protocol.classes[class_id]
    tasks_file = project_root / str(spec["tasks_file"])
    task_ids = list(spec["task_ids"])
    dimension = spec["dimension"]
    if dimension == "eager_vs_lazy":
        return filter_eager_lazy_tasks(load_eager_lazy_tasks(tasks_file), task_ids)
    if dimension == "bfs_vs_dfs":
        return filter_bfs_dfs_tasks(load_bfs_dfs_tasks(tasks_file), task_ids)
    if dimension == "deterministic_vs_randomized":
        return filter_deterministic_randomized_tasks(
            load_deterministic_randomized_tasks(tasks_file), task_ids
        )
    raise ValueError(dimension)


def generate_pilot_artifacts(
    project_root: Path,
    *,
    protocol: PilotProtocol = PILOT_PROTOCOL,
    overwrite: bool = False,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    models_cfg = load_yaml(project_root / "configs" / "models.yaml")["providers"]
    ollama_cfg = models_cfg.get("ollama", {})
    base_url = ollama_cfg.get("base_url", "http://localhost:11434")
    timeout = float(ollama_cfg.get("generate_timeout_seconds", 900))
    max_retries = int(ollama_cfg.get("max_retries", 2))

    plan: list[dict[str, Any]] = []
    clients: dict[tuple[str, float], OllamaClient] = {}

    for class_id in protocol.classes:
        tasks = _load_tasks(protocol, project_root, class_id)
        poles = tuple(protocol.classes[class_id]["poles"])
        for model in protocol.models:
            for temperature in protocol.temperatures:
                for task in tasks:
                    for pole in poles:
                        for rep in range(1, protocol.repetitions + 1):
                            plan.append(
                                {
                                    "class_id": class_id,
                                    "model": model,
                                    "temperature": temperature,
                                    "task_id": task.task_id,
                                    "requested_pole": pole,
                                    "rep": rep,
                                    "task": task,
                                }
                            )

    if dry_run:
        print(f"planned_generations={len(plan)}")
        return plan

    protocol.data_root(project_root).mkdir(parents=True, exist_ok=True)

    for item in plan:
        raw_path, code_path = _artifact_paths(
            protocol,
            project_root=project_root,
            model=item["model"],
            class_id=item["class_id"],
            task_id=item["task_id"],
            pole=item["requested_pole"],
            temperature=item["temperature"],
            rep=item["rep"],
        )
        if raw_path.exists() and code_path.exists() and not overwrite:
            continue

        ollama_model = parse_ollama_model(item["model"])
        if ollama_model is None:
            raise ValueError(item["model"])
        key = (ollama_model, item["temperature"])
        if key not in clients:
            clients[key] = OllamaClient(
                model=ollama_model,
                temperature=item["temperature"],
                base_url=base_url,
                generate_timeout=timeout,
                max_retries=max_retries,
            )
        client = clients[key]
        prompt = _build_prompt(
            protocol, project_root, item["class_id"], item["task"], item["requested_pole"]
        )
        print(
            f"GEN {item['class_id']} {item['task_id']} {item['requested_pole']} "
            f"{item['model']} T={item['temperature']} rep={item['rep']}",
            flush=True,
        )
        response = client.generate(prompt)
        code = extract_code(response)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "study_id": protocol.study_id,
            "class_id": item["class_id"],
            "model": item["model"],
            "temperature": item["temperature"],
            "task_id": item["task_id"],
            "requested_pole": item["requested_pole"],
            "rep": item["rep"],
            "prompt": prompt,
            "response": response,
        }
        raw_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        code_path.write_text(code, encoding="utf-8")

    return plan
