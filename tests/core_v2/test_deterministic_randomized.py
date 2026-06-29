from __future__ import annotations

from pathlib import Path

import pytest

from invert_core.deterministic_randomized_behavioral import (
    run_deterministic_randomized_behavioral_oracle,
)
from invert_core.deterministic_randomized_tasks import load_deterministic_randomized_tasks
from invert_core.detectors.deterministic_randomized import (
    detect_deterministic_randomized,
    detect_deterministic_randomized_file,
    is_genuine_deterministic,
    is_genuine_randomized,
    pole_manipulation_success,
)
from invert_core.pilot_config import CoreV2PilotConfig, plan_core_v2_generations
from invert_core.randomized_prompts import (
    DETERMINISTIC_RANDOMIZED_METHOD_OPERATIONAL,
    build_deterministic_randomized_generation_prompt,
    build_deterministic_randomized_stub_code,
)
from invert_core.stripping import StripLevel, strip_code
from invert_core.tasks import project_root

FIXTURES = Path(__file__).resolve().parent / "fixtures"
CONFIG = project_root() / "configs" / "core_v2_deterministic_randomized_pilot_local.yaml"
REPAIR_CONFIG = (
    project_root() / "configs" / "core_v2_deterministic_randomized_pilot_local_repair.yaml"
)
TASKS_FILE = project_root() / "data" / "core_v2" / "tasks" / "deterministic_randomized_tasks.json"

STRIP_LEVELS = [
    StripLevel.RAW,
    StripLevel.NO_COMMENTS,
    StripLevel.RENAMED,
    StripLevel.NO_IMPORTS,
    StripLevel.FORMAT_NORMALIZED,
]


def _task(task_id: str = "letters_8"):
    tasks = {t.task_id: t for t in load_deterministic_randomized_tasks(TASKS_FILE)}
    return tasks[task_id]


def test_deterministic_fixture_detected() -> None:
    task = _task()
    code = (FIXTURES / "deterministic_processor.py").read_text(encoding="utf-8")
    result = detect_deterministic_randomized(code, task, mode="primary")
    assert result.method == "deterministic"
    assert result.evidence["unique_trace_count"] == 1
    assert result.evidence["run_count"] == 5
    assert len(result.evidence["traces"]) == 5
    assert all(t == result.evidence["traces"][0] for t in result.evidence["traces"])


def test_randomized_fixture_detected_primary() -> None:
    task = _task()
    code = (FIXTURES / "randomized_processor.py").read_text(encoding="utf-8")
    result = detect_deterministic_randomized(code, task, mode="primary")
    assert result.method == "randomized"
    assert result.evidence["unique_trace_count"] >= 2


def test_randomized_fixture_collapses_fixed_seed_control() -> None:
    task = _task()
    code = (FIXTURES / "randomized_processor.py").read_text(encoding="utf-8")
    result = detect_deterministic_randomized(code, task, mode="fixed_seed_control")
    assert result.evidence["unique_trace_count"] == 1
    assert result.method in ("deterministic", "ambiguous")


def test_invalid_fixture_behavioral_fail() -> None:
    task = _task()
    code = (FIXTURES / "invalid_processor.py").read_text(encoding="utf-8")
    behavioral = run_deterministic_randomized_behavioral_oracle(code, task)
    assert not behavioral.parsed
    result = detect_deterministic_randomized(code, task)
    assert result.method == "ambiguous"


def test_stripping_preserves_public_api() -> None:
    code = (FIXTURES / "deterministic_processor.py").read_text(encoding="utf-8")
    renamed = strip_code(code, StripLevel.RENAMED, dimension="deterministic_vs_randomized")
    assert "class ItemProcessor" in renamed
    assert "def process_all" in renamed
    assert "items" in renamed
    assert "visit_fn" in renamed
    assert "seed" in renamed
    assert "ordered" not in renamed


def test_stripping_renames_internals_randomized() -> None:
    code = (FIXTURES / "randomized_processor.py").read_text(encoding="utf-8")
    renamed = strip_code(code, StripLevel.RENAMED, dimension="deterministic_vs_randomized")
    assert "order" not in renamed


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("deterministic_processor.py", "deterministic"),
        ("randomized_processor.py", "randomized"),
    ],
)
def test_detector_survives_strip_levels(fixture: str, expected: str) -> None:
    task = _task()
    code = (FIXTURES / fixture).read_text(encoding="utf-8")
    for level in STRIP_LEVELS:
        stripped = strip_code(code, level, dimension="deterministic_vs_randomized")
        result = detect_deterministic_randomized(stripped, task, mode="primary")
        assert result.method == expected, level.value


def test_detect_file_cli() -> None:
    result = detect_deterministic_randomized_file(
        str(FIXTURES / "deterministic_processor.py"),
        task_id="letters_8",
    )
    payload = result.to_dict()
    assert payload["method"] == "deterministic"
    assert "traces" in payload["evidence"]
    assert "unique_trace_count" in payload["evidence"]
    assert "reason" in payload["evidence"]


def test_pilot_expected_generations() -> None:
    pilot = CoreV2PilotConfig.from_yaml(CONFIG, project_root())
    items = plan_core_v2_generations(pilot, pilot.load_tasks())
    assert pilot.expected_generations() == 120
    assert len(items) == 120


def test_repair_pilot_expected_generations() -> None:
    pilot = CoreV2PilotConfig.from_yaml(REPAIR_CONFIG, project_root())
    items = plan_core_v2_generations(pilot, pilot.load_tasks())
    assert pilot.expected_generations() == 54
    assert len(items) == 54


def test_prompts_include_operational_definitions() -> None:
    tasks = load_deterministic_randomized_tasks(TASKS_FILE)
    for task in tasks:
        for method in ("deterministic", "randomized"):
            prompt = build_deterministic_randomized_generation_prompt(task, method)
            assert DETERMINISTIC_RANDOMIZED_METHOD_OPERATIONAL[method] in prompt
            assert "class ItemProcessor:" in prompt
            assert "visit_fn" in prompt
            assert "process_fn" not in prompt


@pytest.mark.parametrize("method", ["deterministic", "randomized"])
def test_stub_codes_pass_behavioral_and_detector(method: str) -> None:
    tasks = load_deterministic_randomized_tasks(TASKS_FILE)
    for task in tasks:
        code = build_deterministic_randomized_stub_code(task, method)
        behavioral = run_deterministic_randomized_behavioral_oracle(code, task)
        assert behavioral.behavioral_pass, task.task_id
        detected = detect_deterministic_randomized(code, task, mode="primary")
        assert detected.method == method, task.task_id


def test_genuine_pole_flags() -> None:
    task = _task()
    det = detect_deterministic_randomized(
        (FIXTURES / "deterministic_processor.py").read_text(encoding="utf-8"),
        task,
    )
    rand = detect_deterministic_randomized(
        (FIXTURES / "randomized_processor.py").read_text(encoding="utf-8"),
        task,
    )
    assert is_genuine_deterministic(det.evidence)
    assert pole_manipulation_success("deterministic", det.evidence)
    assert is_genuine_randomized(rand.evidence)
    assert pole_manipulation_success("randomized", rand.evidence)


def test_seeded_randomized_reproducible() -> None:
    task = _task()
    code = (FIXTURES / "randomized_seeded_processor.py").read_text(encoding="utf-8")
    result = detect_deterministic_randomized(code, task, mode="fixed_seed_control")
    assert result.evidence["unique_trace_count"] == 1
