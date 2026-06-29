from __future__ import annotations

from pathlib import Path

import pytest

from invert_core.detectors.bfs_dfs import detect_bfs_dfs
from invert_core.stripping import StripLevel, strip_code
from invert_core.bfs_dfs_tasks import load_bfs_dfs_tasks
from invert_core.tasks import project_root

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TASKS_FILE = project_root() / "data" / "core_v2" / "tasks" / "bfs_dfs_tasks.json"


def test_bfs_dfs_stripping_preserves_public_api() -> None:
    code = (FIXTURES / "bfs_traversal.py").read_text(encoding="utf-8")
    stripped = strip_code(code, StripLevel.RENAMED, dimension="bfs_vs_dfs")
    assert "class GraphTraversal:" in stripped
    assert "def reachable_nodes(self):" in stripped
    assert "def __init__(self, graph, start, visit_fn):" in stripped
    assert "x0" in stripped or "x1" in stripped


def test_bfs_dfs_stripping_renames_internals() -> None:
    code = (FIXTURES / "bfs_traversal.py").read_text(encoding="utf-8")
    stripped = strip_code(code, StripLevel.RENAMED, dimension="bfs_vs_dfs")
    assert "visited" not in stripped
    assert "queue" not in stripped
    assert "order" not in stripped


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("bfs_traversal.py", "bfs"),
        ("dfs_traversal.py", "dfs"),
    ],
)
def test_bfs_dfs_detector_on_stripped_with_public_api(fixture: str, expected: str) -> None:
    task = load_bfs_dfs_tasks(TASKS_FILE)[0]
    code = (FIXTURES / fixture).read_text(encoding="utf-8")
    for level in (
        StripLevel.RENAMED,
        StripLevel.NO_IMPORTS,
        StripLevel.FORMAT_NORMALIZED,
    ):
        stripped = strip_code(code, level, dimension="bfs_vs_dfs")
        result = detect_bfs_dfs(stripped, task)
        assert result.method == expected, level.value


@pytest.mark.parametrize(
    "fixture",
    ["linear_chain_bfs.py", "linear_chain_dfs.py"],
)
def test_linear_chain_still_ambiguous_after_public_api_strip(fixture: str) -> None:
    tasks = {t.task_id: t for t in load_bfs_dfs_tasks(TASKS_FILE)}
    linear = tasks["linear_chain"]
    code = (FIXTURES / fixture).read_text(encoding="utf-8")
    stripped = strip_code(code, StripLevel.FORMAT_NORMALIZED, dimension="bfs_vs_dfs")
    result = detect_bfs_dfs(stripped, linear)
    assert result.method == "ambiguous"


def test_eager_lazy_stripping_preserves_public_api() -> None:
    code = (FIXTURES / "lazy_pipeline.py").read_text(encoding="utf-8")
    stripped = strip_code(code, StripLevel.RENAMED, dimension="eager_vs_lazy")
    assert "class FeaturePipeline:" in stripped
    assert "def get_feature_a(self):" in stripped
    assert "feature_a_fn" in stripped


def test_pilot_artifact_survives_dynamic_strip_levels() -> None:
    from invert_core.tasks import project_root

    code_path = (
        project_root()
        / "data/core_v2/code/core_v2_bfs_dfs_pilot_local_001/ollama__devstral__latest/branching_1/bfs/rep_1.py"
    )
    if not code_path.exists():
        pytest.skip("pilot artifacts not present")
    task = load_bfs_dfs_tasks(TASKS_FILE)[0]
    code = code_path.read_text(encoding="utf-8")
    for level in (
        StripLevel.RENAMED,
        StripLevel.NO_IMPORTS,
        StripLevel.FORMAT_NORMALIZED,
    ):
        stripped = strip_code(code, level, dimension="bfs_vs_dfs")
        result = detect_bfs_dfs(stripped, task)
        assert result.method == "bfs", level.value
