from __future__ import annotations

from pathlib import Path

import pytest

from invert_core.detectors.quadrature import detect_quadrature, detect_quadrature_file
from invert_core.pilot_config import CoreV2PilotConfig, plan_core_v2_generations
from invert_core.quadrature_behavioral import run_quadrature_behavioral_oracle
from invert_core.quadrature_prompts import (
    QUADRATURE_METHOD_OPERATIONAL,
    build_quadrature_generation_prompt,
    build_quadrature_stub_code,
)
from invert_core.quadrature_tasks import load_quadrature_tasks
from invert_core.stripping import StripLevel, strip_code
from invert_core.tasks import project_root

FIXTURES = Path(__file__).resolve().parent / "fixtures"
QUADRATURE_CONFIG = project_root() / "configs" / "core_v2_quadrature_pilot_local.yaml"
TASKS_FILE = project_root() / "data" / "core_v2" / "tasks" / "quadrature_tasks.json"

STRIP_LEVELS = [
    StripLevel.RAW,
    StripLevel.NO_COMMENTS,
    StripLevel.RENAMED,
    StripLevel.NO_IMPORTS,
    StripLevel.FORMAT_NORMALIZED,
]


def _entry_for_level(level: StripLevel, *, renamed: str | None = None) -> str | None:
    if level in (StripLevel.RAW, StripLevel.NO_COMMENTS):
        return renamed or "integrate"
    return None


@pytest.mark.parametrize(
    ("fixture", "expected", "entry"),
    [
        ("trapezoidal_basic.py", "trapezoidal", "integrate"),
        ("simpson_basic.py", "simpson", "integrate"),
        ("simpson_loop_weights.py", "simpson", "integrate"),
    ],
)
def test_detect_handcrafted_fixtures(fixture: str, expected: str, entry: str) -> None:
    code = (FIXTURES / fixture).read_text(encoding="utf-8")
    result = detect_quadrature(code, entry_function=entry)
    assert result.method == expected


def test_detect_trapezoidal_renamed() -> None:
    code = (FIXTURES / "trapezoidal_renamed.py").read_text(encoding="utf-8")
    result = detect_quadrature(code, entry_function="x7")
    assert result.method == "trapezoidal"


@pytest.mark.parametrize(
    ("fixture", "expected", "entry"),
    [
        ("trapezoidal_basic.py", "trapezoidal", "integrate"),
        ("simpson_basic.py", "simpson", "integrate"),
    ],
)
def test_survives_all_strip_levels(fixture: str, expected: str, entry: str) -> None:
    code = (FIXTURES / fixture).read_text(encoding="utf-8")
    for level in STRIP_LEVELS:
        stripped = strip_code(code, level)
        ef = _entry_for_level(level, renamed=entry)
        result = detect_quadrature(stripped, entry_function=ef)
        assert result.method == expected, level.value


def test_renamed_fixture_survives_stripping() -> None:
    code = (FIXTURES / "trapezoidal_renamed.py").read_text(encoding="utf-8")
    for level in STRIP_LEVELS:
        stripped = strip_code(code, level)
        result = detect_quadrature(stripped, entry_function=None)
        assert result.method == "trapezoidal", level.value


def test_ambiguous_fixture() -> None:
    code = (FIXTURES / "quadrature_ambiguous.py").read_text(encoding="utf-8")
    result = detect_quadrature(code, entry_function="integrate")
    assert result.method == "ambiguous"


def test_detect_quadrature_file_cli_shape() -> None:
    result = detect_quadrature_file(str(FIXTURES / "trapezoidal_basic.py"), entry_function="integrate")
    payload = result.to_dict()
    assert payload["method"] == "trapezoidal"
    assert "evidence" in payload
    assert "has_endpoint_half_weights" in payload["evidence"]
    assert "has_simpson_4_2_pattern" in payload["evidence"]
    assert "coefficient_literals" in payload["evidence"]
    assert "function_eval_pattern" in payload["evidence"]
    assert "reason" in payload["evidence"]


def test_quadrature_pilot_expected_generations() -> None:
    pilot = CoreV2PilotConfig.from_yaml(QUADRATURE_CONFIG, project_root())
    items = plan_core_v2_generations(pilot, pilot.load_tasks())
    assert pilot.expected_generations() == 54
    assert len(items) == 54


def test_quadrature_prompts_include_operational_definitions() -> None:
    tasks = load_quadrature_tasks(TASKS_FILE)
    for task in tasks:
        trap_prompt = build_quadrature_generation_prompt(task, "trapezoidal")
        simp_prompt = build_quadrature_generation_prompt(task, "simpson")
        assert QUADRATURE_METHOD_OPERATIONAL["trapezoidal"] in trap_prompt
        assert QUADRATURE_METHOD_OPERATIONAL["simpson"] in simp_prompt
        assert "def integrate(f, a, b, n):" in trap_prompt


@pytest.mark.parametrize("method", ["trapezoidal", "simpson"])
def test_quadrature_stub_codes_pass_behavioral_oracle(method: str) -> None:
    tasks = load_quadrature_tasks(TASKS_FILE)
    for task in tasks:
        code = build_quadrature_stub_code(task, method)
        result = run_quadrature_behavioral_oracle(code, task)
        assert result.parsed, task.task_id
        assert result.behavioral_pass, f"{task.task_id}: {result.error}"
