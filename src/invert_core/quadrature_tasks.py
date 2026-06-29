from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class QuadratureTask:
    task_id: str
    entry_function: str
    integrand: str
    a: float
    b: float
    n: int
    expected_value: float
    behavioral_tolerance: float
    integrand_type: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuadratureTask:
        return cls(
            task_id=data["task_id"],
            entry_function=data["entry_function"],
            integrand=data["integrand"],
            a=float(data["a"]),
            b=float(data["b"]),
            n=int(data["n"]),
            expected_value=float(data["expected_value"]),
            behavioral_tolerance=float(data["behavioral_tolerance"]),
            integrand_type=data.get("integrand_type", "custom"),
        )


def load_quadrature_tasks(path: Path | str) -> list[QuadratureTask]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [QuadratureTask.from_dict(item) for item in raw["tasks"]]


def filter_quadrature_tasks(tasks: list[QuadratureTask], task_ids: list[str]) -> list[QuadratureTask]:
    by_id = {t.task_id: t for t in tasks}
    missing = [tid for tid in task_ids if tid not in by_id]
    if missing:
        raise ValueError(f"Unknown task IDs: {missing}")
    return [by_id[tid] for tid in task_ids]
