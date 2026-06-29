from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class OdeTask:
    task_id: str
    entry_function: str
    state_dimension: int
    equation: str
    parameters: dict[str, float]
    initial_condition: list[float]
    t0: float
    t1: float
    dt: float
    expected_behavior: str
    behavioral_tolerance: float
    reference_type: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OdeTask:
        return cls(
            task_id=data["task_id"],
            entry_function=data["entry_function"],
            state_dimension=int(data["state_dimension"]),
            equation=data["equation"],
            parameters={k: float(v) for k, v in data["parameters"].items()},
            initial_condition=[float(v) for v in data["initial_condition"]],
            t0=float(data["t0"]),
            t1=float(data["t1"]),
            dt=float(data["dt"]),
            expected_behavior=data["expected_behavior"],
            behavioral_tolerance=float(data["behavioral_tolerance"]),
            reference_type=data["reference_type"],
        )

    @property
    def y0(self) -> float | list[float]:
        if self.state_dimension == 1:
            return self.initial_condition[0]
        return list(self.initial_condition)

    def parameter_summary(self) -> str:
        parts = [f"{k}={v}" for k, v in sorted(self.parameters.items())]
        return ", ".join(parts)


def load_ode_tasks(path: Path | str) -> list[OdeTask]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [OdeTask.from_dict(item) for item in raw["tasks"]]


def filter_ode_tasks(tasks: list[OdeTask], task_ids: list[str]) -> list[OdeTask]:
    by_id = {t.task_id: t for t in tasks}
    missing = [tid for tid in task_ids if tid not in by_id]
    if missing:
        raise ValueError(f"Unknown task IDs: {missing}")
    return [by_id[tid] for tid in task_ids]
