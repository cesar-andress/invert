from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PilotProtocol:
    study_id: str
    research_question: str
    models: tuple[str, ...]
    temperatures: tuple[float, ...]
    repetitions: int
    strip_levels: tuple[str, ...]
    classes: dict[str, dict[str, object]]

    @property
    def data_root_name(self) -> str:
        return "h01_temperature_pilot"

    def data_root(self, project_root: Path) -> Path:
        return project_root / "data" / "discovery" / self.data_root_name

    def results_dir(self, project_root: Path) -> Path:
        return project_root / "results" / "research_extension" / "H01_temperature"


PILOT_PROTOCOL = PilotProtocol(
    study_id="H01_temperature_pilot",
    research_question=(
        "Does decoding temperature increase process-level diversity while preserving "
        "behavioral correctness and requested process poles?"
    ),
    models=(
        "ollama:qwen2.5-coder:14b",
        "ollama:qwen3-coder:30b",
    ),
    temperatures=(0.0, 0.4, 0.8),
    repetitions=10,
    strip_levels=("raw",),
    classes={
        "C": {
            "dimension": "eager_vs_lazy",
            "tasks_file": "data/core_v2/tasks/eager_lazy_tasks.json",
            "task_ids": ("mixed_signed_vector", "small_positive_vector"),
            "poles": ("eager", "lazy"),
        },
        "D": {
            "dimension": "bfs_vs_dfs",
            "tasks_file": "data/core_v2/tasks/bfs_dfs_tasks.json",
            "task_ids": ("branching_1", "linear_chain"),
            "poles": ("bfs", "dfs"),
        },
        "E": {
            "dimension": "deterministic_vs_randomized",
            "tasks_file": "data/core_v2/tasks/deterministic_randomized_tasks.json",
            "task_ids": ("letters_8", "numbers_10"),
            "poles": ("deterministic", "randomized"),
        },
    },
)
