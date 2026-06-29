from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class EagerLazyTask:
    task_id: str
    x: list[int]
    expected_feature_a: int
    expected_feature_b: int
    expected_feature_c: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EagerLazyTask:
        return cls(
            task_id=data["task_id"],
            x=[int(v) for v in data["x"]],
            expected_feature_a=int(data["expected_feature_a"]),
            expected_feature_b=int(data["expected_feature_b"]),
            expected_feature_c=int(data["expected_feature_c"]),
        )


def load_eager_lazy_tasks(path: Path | str) -> list[EagerLazyTask]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [EagerLazyTask.from_dict(item) for item in raw["tasks"]]


def filter_eager_lazy_tasks(
    tasks: list[EagerLazyTask], task_ids: list[str]
) -> list[EagerLazyTask]:
    by_id = {t.task_id: t for t in tasks}
    missing = [tid for tid in task_ids if tid not in by_id]
    if missing:
        raise ValueError(f"Unknown task IDs: {missing}")
    return [by_id[tid] for tid in task_ids]


from typing import Callable


def default_feature_fns() -> tuple[
    Callable[[list[int]], int],
    Callable[[list[int]], int],
    Callable[[list[int]], int],
]:
    def feature_a_fn(x: list[int]) -> int:
        return sum(x_i**2 for x_i in x)

    def feature_b_fn(x: list[int]) -> int:
        return sum(abs(x_i) for x_i in x)

    def feature_c_fn(x: list[int]) -> int:
        return max(x) - min(x)

    return feature_a_fn, feature_b_fn, feature_c_fn
