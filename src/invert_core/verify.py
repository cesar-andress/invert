from __future__ import annotations

from pathlib import Path
from typing import Any

from invert_core.bfs_dfs_tasks import load_bfs_dfs_tasks
from invert_core.deterministic_randomized_tasks import load_deterministic_randomized_tasks
from invert_core.detectors.bfs_dfs import detect_bfs_dfs
from invert_core.detectors.deterministic_randomized import detect_deterministic_randomized
from invert_core.detectors.eager_lazy import detect_eager_lazy
from invert_core.detectors.integration import detect_integration
from invert_core.detectors.lock_control import detect_lock_control
from invert_core.stripping import STANDARD_STRIP_LEVELS, StripLevel, strip_code
from invert_core.tasks import project_root


def verify_integration_detector(
    code: str,
    expected: str,
    *,
    entry_function: str | None = None,
    strip_levels: list[StripLevel] | None = None,
) -> dict[str, Any]:
    """Verify detector returns expected method, optionally across strip levels."""
    levels = strip_levels or STANDARD_STRIP_LEVELS
    results: dict[str, Any] = {"expected": expected, "levels": {}}
    all_match = True

    for level in levels:
        stripped = strip_code(code, level)
        ef = (
            entry_function
            if level in (StripLevel.RAW, StripLevel.NO_COMMENTS)
            else None
        )
        detected = detect_integration(stripped, entry_function=ef)
        match = detected.method == expected
        results["levels"][level.value] = {
            "method": detected.method,
            "match": match,
            "evidence": detected.evidence,
        }
        if not match:
            all_match = False

    results["all_survive"] = all_match
    return results


def verify_lock_detector(code: str, expected: str) -> dict[str, Any]:
    detected = detect_lock_control(code)
    return {
        "expected": expected,
        "method": detected.method,
        "match": detected.method == expected,
        "evidence": detected.to_dict(),
    }


def verify_eager_lazy_detector(
    code: str,
    expected: str,
    *,
    strip_levels: list[StripLevel] | None = None,
) -> dict[str, Any]:
    levels = strip_levels or STANDARD_STRIP_LEVELS
    results: dict[str, Any] = {"expected": expected, "levels": {}}
    all_match = True

    for level in levels:
        stripped = strip_code(code, level, dimension="eager_vs_lazy")
        detected = detect_eager_lazy(stripped)
        match = detected.method == expected
        results["levels"][level.value] = {
            "method": detected.method,
            "match": match,
            "evidence": detected.evidence,
        }
        if not match:
            all_match = False

    results["all_survive"] = all_match
    return results


def verify_bfs_dfs_detector(
    code: str,
    expected: str,
    task_id: str,
    *,
    strip_levels: list[StripLevel] | None = None,
) -> dict[str, Any]:
    tasks_by_id = {
        t.task_id: t
        for t in load_bfs_dfs_tasks(project_root() / "data" / "core_v2" / "tasks" / "bfs_dfs_tasks.json")
    }
    task = tasks_by_id[task_id]
    levels = strip_levels or STANDARD_STRIP_LEVELS
    results: dict[str, Any] = {"expected": expected, "levels": {}}
    all_match = True

    for level in levels:
        stripped = strip_code(code, level, dimension="bfs_vs_dfs")
        detected = detect_bfs_dfs(stripped, task)
        match = detected.method == expected
        results["levels"][level.value] = {
            "method": detected.method,
            "match": match,
            "evidence": detected.evidence,
        }
        if not match:
            all_match = False

    results["all_survive"] = all_match
    return results


def verify_deterministic_randomized_detector(
    code: str,
    expected: str,
    task_id: str,
    *,
    strip_levels: list[StripLevel] | None = None,
) -> dict[str, Any]:
    tasks_by_id = {
        t.task_id: t
        for t in load_deterministic_randomized_tasks(
            project_root() / "data" / "core_v2" / "tasks" / "deterministic_randomized_tasks.json"
        )
    }
    task = tasks_by_id[task_id]
    levels = strip_levels or STANDARD_STRIP_LEVELS
    results: dict[str, Any] = {"expected": expected, "levels": {}}
    all_match = True

    for level in levels:
        stripped = strip_code(code, level, dimension="deterministic_vs_randomized")
        detected = detect_deterministic_randomized(stripped, task, mode="primary")
        match = detected.method == expected
        results["levels"][level.value] = {
            "method": detected.method,
            "match": match,
            "evidence": detected.evidence,
        }
        if not match:
            all_match = False

    results["all_survive"] = all_match
    return results


def verify_fixture_dir(fixtures_dir: Path) -> dict[str, Any]:
    report: dict[str, Any] = {
        "integration": [],
        "lock": [],
        "eager_lazy": [],
        "bfs_dfs": [],
        "deterministic_randomized": [],
        "passed": True,
    }

    euler = fixtures_dir / "euler_m0.py"
    rk4 = fixtures_dir / "rk4_m1.py"
    no_lock = fixtures_dir / "counter_no_lock.py"
    with_lock = fixtures_dir / "counter_with_lock.py"

    if euler.exists():
        r = verify_integration_detector(
            euler.read_text(encoding="utf-8"),
            "euler",
            entry_function="integrate_ode",
        )
        report["integration"].append({"file": "euler_m0.py", **r})
        if not r["all_survive"]:
            report["passed"] = False

    if rk4.exists():
        r = verify_integration_detector(
            rk4.read_text(encoding="utf-8"),
            "rk4",
            entry_function="integrate_ode",
        )
        report["integration"].append({"file": "rk4_m1.py", **r})
        if not r["all_survive"]:
            report["passed"] = False

    if no_lock.exists():
        r = verify_lock_detector(no_lock.read_text(encoding="utf-8"), "no_lock")
        report["lock"].append({"file": "counter_no_lock.py", **r})
        if not r["match"]:
            report["passed"] = False

    if with_lock.exists():
        r = verify_lock_detector(with_lock.read_text(encoding="utf-8"), "locked")
        report["lock"].append({"file": "counter_with_lock.py", **r})
        if not r["match"]:
            report["passed"] = False

    eager_pipeline = fixtures_dir / "eager_pipeline.py"
    lazy_pipeline = fixtures_dir / "lazy_pipeline.py"
    if eager_pipeline.exists():
        r = verify_eager_lazy_detector(
            eager_pipeline.read_text(encoding="utf-8"),
            "eager",
        )
        report["eager_lazy"].append({"file": "eager_pipeline.py", **r})
        if not r["all_survive"]:
            report["passed"] = False

    if lazy_pipeline.exists():
        r = verify_eager_lazy_detector(
            lazy_pipeline.read_text(encoding="utf-8"),
            "lazy",
        )
        report["eager_lazy"].append({"file": "lazy_pipeline.py", **r})
        if not r["all_survive"]:
            report["passed"] = False

    bfs_fixture = fixtures_dir / "bfs_traversal.py"
    dfs_fixture = fixtures_dir / "dfs_traversal.py"
    if bfs_fixture.exists():
        r = verify_bfs_dfs_detector(
            bfs_fixture.read_text(encoding="utf-8"),
            "bfs",
            "branching_1",
        )
        report["bfs_dfs"].append({"file": "bfs_traversal.py", **r})
        if not r["all_survive"]:
            report["passed"] = False

    if dfs_fixture.exists():
        r = verify_bfs_dfs_detector(
            dfs_fixture.read_text(encoding="utf-8"),
            "dfs",
            "branching_1",
        )
        report["bfs_dfs"].append({"file": "dfs_traversal.py", **r})
        if not r["all_survive"]:
            report["passed"] = False

    det_fixture = fixtures_dir / "deterministic_processor.py"
    rand_fixture = fixtures_dir / "randomized_processor.py"
    if det_fixture.exists():
        r = verify_deterministic_randomized_detector(
            det_fixture.read_text(encoding="utf-8"),
            "deterministic",
            "letters_8",
        )
        report["deterministic_randomized"].append({"file": "deterministic_processor.py", **r})
        if not r["all_survive"]:
            report["passed"] = False

    if rand_fixture.exists():
        r = verify_deterministic_randomized_detector(
            rand_fixture.read_text(encoding="utf-8"),
            "randomized",
            "letters_8",
        )
        report["deterministic_randomized"].append({"file": "randomized_processor.py", **r})
        if not r["all_survive"]:
            report["passed"] = False

    return report
