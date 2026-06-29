from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from invert.schemas import load_yaml

from invert_core.bfs_dfs_tasks import BfsDfsTask, filter_bfs_dfs_tasks, load_bfs_dfs_tasks
from invert_core.deterministic_randomized_tasks import (
    DeterministicRandomizedTask,
    filter_deterministic_randomized_tasks,
    load_deterministic_randomized_tasks,
)
from invert_core.eager_lazy_tasks import EagerLazyTask, filter_eager_lazy_tasks, load_eager_lazy_tasks
from invert_core.ode_tasks import OdeTask, filter_ode_tasks, load_ode_tasks
from invert_core.quadrature_tasks import QuadratureTask, filter_quadrature_tasks, load_quadrature_tasks


@dataclass
class CoreV2PilotConfig:
    config_path: Path
    project_root: Path
    run_name: str
    overwrite: bool
    family: str
    dimension: str
    task_ids: list[str]
    tasks_file: Path
    models: list[str]
    repetitions: int
    language: str
    pure_implementation: bool
    methods: list[str]
    strip_levels: list[str]
    models_config: Path

    @classmethod
    def from_yaml(cls, config_path: Path, project_root: Path) -> CoreV2PilotConfig:
        raw = load_yaml(config_path)
        run = raw.get("run", {})
        tasks_raw = raw.get("tasks", {})
        generation = raw.get("generation", {})
        stripping = raw.get("stripping", {})

        tasks_file = project_root / tasks_raw.get(
            "file", "data/core_v2/tasks/euler_rk4_tasks.json"
        )
        models_config = project_root / generation.get("models_config", "configs/models.yaml")

        return cls(
            config_path=config_path,
            project_root=project_root,
            run_name=run.get("name", "unnamed"),
            overwrite=bool(run.get("overwrite", False)),
            family=raw.get("family", "F1"),
            dimension=raw.get("dimension", "euler_vs_rk4"),
            task_ids=list(tasks_raw["include"]),
            tasks_file=tasks_file,
            models=list(generation["models"]),
            repetitions=int(generation["repetitions"]),
            language=generation.get("language", "python"),
            pure_implementation=bool(generation.get("pure_implementation", True)),
            methods=list(raw["methods"]),
            strip_levels=list(stripping.get("levels", [])),
            models_config=models_config,
        )

    def load_tasks(
        self,
    ) -> list[
        OdeTask
        | QuadratureTask
        | EagerLazyTask
        | BfsDfsTask
        | DeterministicRandomizedTask
    ]:
        if self.dimension == "trapezoidal_vs_simpson":
            return filter_quadrature_tasks(
                load_quadrature_tasks(self.tasks_file), self.task_ids
            )
        if self.dimension == "eager_vs_lazy":
            return filter_eager_lazy_tasks(
                load_eager_lazy_tasks(self.tasks_file), self.task_ids
            )
        if self.dimension == "bfs_vs_dfs":
            return filter_bfs_dfs_tasks(
                load_bfs_dfs_tasks(self.tasks_file), self.task_ids
            )
        if self.dimension == "deterministic_vs_randomized":
            return filter_deterministic_randomized_tasks(
                load_deterministic_randomized_tasks(self.tasks_file), self.task_ids
            )
        return filter_ode_tasks(load_ode_tasks(self.tasks_file), self.task_ids)

    @property
    def data_root(self) -> Path:
        return self.project_root / "data" / "core_v2"

    @property
    def results_dir(self) -> Path:
        return self.project_root / "results" / "core_v2" / "runs" / self.run_name

    def expected_generations(self) -> int:
        return (
            len(self.task_ids)
            * len(self.methods)
            * len(self.models)
            * self.repetitions
        )


from invert_core.models import sanitize_model_for_storage


@dataclass
class CoreV2GenerationItem:
    model: str
    task: OdeTask | QuadratureTask | EagerLazyTask | BfsDfsTask | DeterministicRandomizedTask
    method: str
    rep: int
    run_name: str

    @property
    def storage_model(self) -> str:
        return sanitize_model_for_storage(self.model)

    def raw_path(self, data_root: Path) -> Path:
        return (
            data_root
            / "raw"
            / self.run_name
            / self.storage_model
            / self.task.task_id
            / self.method
            / f"rep_{self.rep}.json"
        )

    def code_path(self, data_root: Path) -> Path:
        return (
            data_root
            / "code"
            / self.run_name
            / self.storage_model
            / self.task.task_id
            / self.method
            / f"rep_{self.rep}.py"
        )

    def stripped_path(self, data_root: Path, strip_level: str) -> Path:
        return (
            data_root
            / "stripped"
            / self.run_name
            / strip_level
            / self.storage_model
            / self.task.task_id
            / self.method
            / f"rep_{self.rep}.py"
        )


def plan_core_v2_generations(
    pilot: CoreV2PilotConfig, tasks: list[OdeTask | QuadratureTask | EagerLazyTask | BfsDfsTask]
) -> list[CoreV2GenerationItem]:
    items: list[CoreV2GenerationItem] = []
    for model in pilot.models:
        for task in tasks:
            for method in pilot.methods:
                for rep in range(1, pilot.repetitions + 1):
                    items.append(
                        CoreV2GenerationItem(
                            model=model,
                            task=task,
                            method=method,
                            rep=rep,
                            run_name=pilot.run_name,
                        )
                    )
    return items
