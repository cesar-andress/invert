from __future__ import annotations

from pathlib import Path

import pytest

from invert_core.bfs_dfs_behavioral import run_bfs_dfs_behavioral_oracle
from invert_core.bfs_dfs_prompts import (
    BFS_DFS_METHOD_OPERATIONAL,
    build_bfs_dfs_generation_prompt,
    build_bfs_dfs_stub_code,
)
from invert_core.bfs_dfs_tasks import load_bfs_dfs_tasks
from invert_core.detectors.bfs_dfs import (
    detect_bfs_dfs,
    detect_bfs_dfs_file,
    is_genuine_bfs,
    is_genuine_dfs,
    pole_manipulation_success,
)
from invert_core.pilot_config import CoreV2PilotConfig, plan_core_v2_generations
from invert_core.stripping import StripLevel, strip_code
from invert_core.tasks import project_root

FIXTURES = Path(__file__).resolve().parent / "fixtures"
BFS_DFS_CONFIG = project_root() / "configs" / "core_v2_bfs_dfs_pilot_local.yaml"
TASKS_FILE = project_root() / "data" / "core_v2" / "tasks" / "bfs_dfs_tasks.json"

STRIP_LEVELS = [
    StripLevel.RAW,
    StripLevel.NO_COMMENTS,
    StripLevel.RENAMED,
    StripLevel.NO_IMPORTS,
    StripLevel.FORMAT_NORMALIZED,
]


def _branching_task():
    return load_bfs_dfs_tasks(TASKS_FILE)[0]


def test_detect_bfs_fixture_branching_1() -> None:
    task = _branching_task()
    code = (FIXTURES / "bfs_traversal.py").read_text(encoding="utf-8")
    result = detect_bfs_dfs(code, task)
    assert result.method == "bfs"
    assert result.evidence["visit_trace"] == task.expected_bfs_order
    assert result.evidence["bfs_order_match"] is True
    assert result.evidence["dfs_order_match"] is False


def test_detect_dfs_fixture_branching_1() -> None:
    task = _branching_task()
    code = (FIXTURES / "dfs_traversal.py").read_text(encoding="utf-8")
    result = detect_bfs_dfs(code, task)
    assert result.method == "dfs"
    assert result.evidence["visit_trace"] == task.expected_dfs_order
    assert result.evidence["dfs_order_match"] is True
    assert result.evidence["bfs_order_match"] is False


@pytest.mark.parametrize(
    "fixture",
    ["linear_chain_bfs.py", "linear_chain_dfs.py"],
)
def test_linear_chain_is_ambiguous(fixture: str) -> None:
    tasks = {t.task_id: t for t in load_bfs_dfs_tasks(TASKS_FILE)}
    task = tasks["linear_chain"]
    code = (FIXTURES / fixture).read_text(encoding="utf-8")
    result = detect_bfs_dfs(code, task)
    assert result.method == "ambiguous"
    assert result.evidence["bfs_order_match"] is True
    assert result.evidence["dfs_order_match"] is True
    assert result.evidence["reason"] == "visit_trace_matches_bfs_and_dfs"


def test_invalid_fixture_behavioral_fail() -> None:
    task = _branching_task()
    code = (FIXTURES / "invalid_graph_traversal.py").read_text(encoding="utf-8")
    behavioral = run_bfs_dfs_behavioral_oracle(code, task)
    assert not behavioral.parsed
    result = detect_bfs_dfs(code, task)
    assert result.method == "ambiguous"


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("bfs_traversal.py", "bfs"),
        ("dfs_traversal.py", "dfs"),
    ],
)
def test_survives_all_strip_levels(fixture: str, expected: str) -> None:
    task = _branching_task()
    code = (FIXTURES / fixture).read_text(encoding="utf-8")
    for level in STRIP_LEVELS:
        stripped = strip_code(code, level, dimension="bfs_vs_dfs")
        result = detect_bfs_dfs(stripped, task)
        assert result.method == expected, level.value


def test_trace_matches_expected_bfs_order() -> None:
    task = _branching_task()
    code = (FIXTURES / "bfs_traversal.py").read_text(encoding="utf-8")
    result = detect_bfs_dfs(code, task)
    assert result.evidence["visit_trace"] == ["A", "B", "C", "D", "E", "F"]


def test_trace_matches_expected_dfs_order() -> None:
    task = _branching_task()
    code = (FIXTURES / "dfs_traversal.py").read_text(encoding="utf-8")
    result = detect_bfs_dfs(code, task)
    assert result.evidence["visit_trace"] == ["A", "B", "D", "E", "C", "F"]


def test_detect_bfs_dfs_file_cli() -> None:
    result = detect_bfs_dfs_file(str(FIXTURES / "bfs_traversal.py"), task_id="branching_1")
    payload = result.to_dict()
    assert payload["method"] == "bfs"
    assert "visit_trace" in payload["evidence"]
    assert "expected_reachable" in payload["evidence"]
    assert "reason" in payload["evidence"]


def test_bfs_dfs_pilot_expected_generations() -> None:
    pilot = CoreV2PilotConfig.from_yaml(BFS_DFS_CONFIG, project_root())
    items = plan_core_v2_generations(pilot, pilot.load_tasks())
    assert pilot.expected_generations() == 120
    assert len(items) == 120


def test_bfs_dfs_prompts_include_operational_definitions() -> None:
    tasks = load_bfs_dfs_tasks(TASKS_FILE)
    branching = [t for t in tasks if not t.is_negative_control]
    for task in branching:
        bfs_prompt = build_bfs_dfs_generation_prompt(task, "bfs")
        dfs_prompt = build_bfs_dfs_generation_prompt(task, "dfs")
        assert BFS_DFS_METHOD_OPERATIONAL["bfs"] in bfs_prompt
        assert BFS_DFS_METHOD_OPERATIONAL["dfs"] in dfs_prompt
        assert "class GraphTraversal:" in bfs_prompt


@pytest.mark.parametrize("method", ["bfs", "dfs"])
def test_stub_codes_pass_behavioral_and_detector(method: str) -> None:
    tasks = [t for t in load_bfs_dfs_tasks(TASKS_FILE) if not t.is_negative_control]
    for task in tasks:
        code = build_bfs_dfs_stub_code(task, method)
        behavioral = run_bfs_dfs_behavioral_oracle(code, task)
        assert behavioral.behavioral_pass, task.task_id
        detected = detect_bfs_dfs(code, task)
        assert detected.method == method, task.task_id


def test_genuine_pole_flags() -> None:
    task = _branching_task()
    bfs = detect_bfs_dfs((FIXTURES / "bfs_traversal.py").read_text(encoding="utf-8"), task)
    dfs = detect_bfs_dfs((FIXTURES / "dfs_traversal.py").read_text(encoding="utf-8"), task)
    assert is_genuine_bfs(bfs.evidence)
    assert pole_manipulation_success("bfs", bfs.evidence)
    assert is_genuine_dfs(dfs.evidence)
    assert pole_manipulation_success("dfs", dfs.evidence)


def test_negative_control_stubs_ambiguous() -> None:
    tasks = {t.task_id: t for t in load_bfs_dfs_tasks(TASKS_FILE)}
    linear = tasks["linear_chain"]
    for method in ("bfs", "dfs"):
        code = build_bfs_dfs_stub_code(linear, method)
        result = detect_bfs_dfs(code, linear)
        assert result.method == "ambiguous"
