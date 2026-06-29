from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CoreTask:
    task_id: str
    entry_function: str
    dimension: str
    m0_label: str
    m1_label: str
    functional_behavior: str
    tolerance: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CoreTask:
        return cls(
            task_id=data["task_id"],
            entry_function=data["entry_function"],
            dimension=data["dimension"],
            m0_label=data["m0_label"],
            m1_label=data["m1_label"],
            functional_behavior=data["functional_behavior"],
            tolerance=data.get("tolerance", "1e-3"),
        )


def load_core_tasks(path: Path | str) -> list[CoreTask]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [CoreTask.from_dict(item) for item in raw["tasks"]]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def prereg_dir() -> Path:
    return project_root() / "prereg"


def results_dir() -> Path:
    return project_root() / "results" / "core_v2"


def fixtures_dir() -> Path:
    return project_root() / "tests" / "core_v2" / "fixtures"
