from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DeterministicRandomizedTask:
    task_id: str
    items: list[Any]
    control_family: str = "primary"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeterministicRandomizedTask:
        return cls(
            task_id=data["task_id"],
            items=list(data["items"]),
            control_family=data.get("control_family", "primary"),
        )

    @property
    def expected_items(self) -> list[Any]:
        return list(self.items)

    @property
    def is_primary(self) -> bool:
        return self.control_family == "primary"


@dataclass
class DeterministicRandomizedTaskFile:
    tasks: list[DeterministicRandomizedTask]
    fixed_seed: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeterministicRandomizedTaskFile:
        control = data.get("fixed_seed_control", {})
        return cls(
            tasks=[DeterministicRandomizedTask.from_dict(item) for item in data["tasks"]],
            fixed_seed=int(control.get("seed", 12345)),
        )


def load_deterministic_randomized_tasks(path: Path | str) -> list[DeterministicRandomizedTask]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return DeterministicRandomizedTaskFile.from_dict(raw).tasks


def load_deterministic_randomized_task_file(path: Path | str) -> DeterministicRandomizedTaskFile:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return DeterministicRandomizedTaskFile.from_dict(raw)


def filter_deterministic_randomized_tasks(
    tasks: list[DeterministicRandomizedTask], task_ids: list[str]
) -> list[DeterministicRandomizedTask]:
    by_id = {t.task_id: t for t in tasks}
    missing = [tid for tid in task_ids if tid not in by_id]
    if missing:
        raise ValueError(f"Unknown task IDs: {missing}")
    return [by_id[tid] for tid in task_ids]
