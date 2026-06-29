from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from invert.schemas import Task, load_tasks, load_yaml


@dataclass
class PilotConfig:
    config_path: Path
    run_name: str
    task_ids: list[str]
    generator_models: list[str]
    judge_models: list[str]
    repetitions: int
    max_generations: int
    overwrite: bool
    tasks_file: Path

    @classmethod
    def from_yaml(cls, config_path: Path, project_root: Path) -> PilotConfig:
        raw = load_yaml(config_path)
        tasks_file = project_root / "data" / "intents" / "tasks.json"
        run = raw.get("run", {})
        return cls(
            config_path=config_path,
            run_name=run.get("name", "unnamed"),
            task_ids=list(raw["tasks"]["include"]),
            generator_models=list(raw["generation"]["models"]),
            judge_models=list(raw["recovery"]["judge_models"]),
            repetitions=int(raw["generation"]["repetitions"]),
            max_generations=int(run.get("max_generations", 0)),
            overwrite=bool(run.get("overwrite", False)),
            tasks_file=tasks_file,
        )

    def filter_tasks(self, all_tasks: list[Task]) -> list[Task]:
        by_id = {t.task_id: t for t in all_tasks}
        missing = [tid for tid in self.task_ids if tid not in by_id]
        if missing:
            raise ValueError(f"Unknown task IDs in config: {missing}")
        return [by_id[tid] for tid in self.task_ids]

    @property
    def run_dir(self) -> Path:
        return self.config_path.resolve().parents[1] / "results" / "runs" / self.run_name


def get_git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def write_run_metadata(
    pilot: PilotConfig,
    models_config_path: Path,
    project_root: Path,
    started_at: datetime | None = None,
) -> Path:
    models_cfg = load_yaml(models_config_path)["providers"]
    temps = [
        models_cfg[m].get("temperature", 0)
        for m in pilot.generator_models
        if m in models_cfg
    ]
    temperature = temps[0] if temps else 0

    try:
        config_file = str(pilot.config_path.resolve().relative_to(project_root.resolve()))
    except ValueError:
        config_file = str(pilot.config_path)

    metadata = {
        "run_name": pilot.run_name,
        "started_at": (started_at or datetime.now(timezone.utc)).isoformat(),
        "tasks": pilot.task_ids,
        "generator_models": pilot.generator_models,
        "judge_models": pilot.judge_models,
        "repetitions": pilot.repetitions,
        "temperature": temperature,
        "max_generations": pilot.max_generations,
        "git_commit": get_git_commit(),
        "config_file": config_file,
    }

    out_dir = project_root / "results" / "runs" / pilot.run_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "metadata.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    return out_path


def load_run_metadata(project_root: Path, run_name: str) -> dict[str, Any]:
    path = project_root / "results" / "runs" / run_name / "metadata.json"
    if not path.exists():
        raise FileNotFoundError(f"Run metadata not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@dataclass
class GenerationItem:
    model: str
    task: Task
    dimension: str
    value: str
    rep: int

    @property
    def raw_path(self) -> Path:
        raise NotImplementedError

    def paths(self, data_dir: Path) -> tuple[Path, Path]:
        raw = (
            data_dir
            / "raw"
            / self.model
            / self.task.task_id
            / self.dimension
            / self.value
            / f"rep_{self.rep}.json"
        )
        code = (
            data_dir
            / "code"
            / self.model
            / self.task.task_id
            / self.dimension
            / self.value
            / f"rep_{self.rep}.py"
        )
        return raw, code


def plan_generations(
    tasks: list[Task],
    models: list[str],
    repetitions: int,
) -> list[GenerationItem]:
    items: list[GenerationItem] = []
    for model in models:
        for task in tasks:
            for dimension in task.dimensions:
                for value in ("v0", "v1"):
                    for rep in range(1, repetitions + 1):
                        items.append(
                            GenerationItem(
                                model=model,
                                task=task,
                                dimension=dimension,
                                value=value,
                                rep=rep,
                            )
                        )
    return items
