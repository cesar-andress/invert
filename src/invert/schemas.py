from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DIMENSION_NAMES = [
    "performance",
    "security",
    "error_handling",
    "api_preference",
    "readability",
    "maintainability",
    "edge_cases",
    "concurrency",
]


@dataclass
class DimensionSpec:
    v0: str
    v1: str


@dataclass
class Task:
    task_id: str
    language: str
    functional_behavior: str
    dimensions: dict[str, DimensionSpec] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        dimensions = {
            name: DimensionSpec(v0=spec["v0"], v1=spec["v1"])
            for name, spec in data["dimensions"].items()
        }
        return cls(
            task_id=data["task_id"],
            language=data["language"],
            functional_behavior=data["functional_behavior"],
            dimensions=dimensions,
        )

    def default_dimension_values(self) -> dict[str, str]:
        return {name: "v0" for name in self.dimensions}


def load_tasks(path: Path | str) -> list[Task]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, list):
        return [Task.from_dict(item) for item in raw]
    return [Task.from_dict(raw)]


def load_yaml(path: Path | str) -> dict[str, Any]:
    import yaml

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
