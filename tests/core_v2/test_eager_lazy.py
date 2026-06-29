from __future__ import annotations

import json
from pathlib import Path

import pytest

from invert_core.detectors.eager_lazy import detect_eager_lazy, detect_eager_lazy_file
from invert_core.eager_lazy_behavioral import run_eager_lazy_behavioral_oracle
from invert_core.eager_lazy_prompts import (
    EAGER_LAZY_METHOD_OPERATIONAL,
    build_eager_lazy_generation_prompt,
    build_eager_lazy_stub_code,
)
from invert_core.eager_lazy_tasks import load_eager_lazy_tasks
from invert_core.pilot_config import CoreV2PilotConfig, plan_core_v2_generations
from invert_core.stripping import StripLevel, strip_code
from invert_core.tasks import project_root

FIXTURES = Path(__file__).resolve().parent / "fixtures"
EAGER_LAZY_CONFIG = project_root() / "configs" / "core_v2_eager_lazy_pilot_local.yaml"
TASKS_FILE = project_root() / "data" / "core_v2" / "tasks" / "eager_lazy_tasks.json"

STRIP_LEVELS = [
    StripLevel.RAW,
    StripLevel.NO_COMMENTS,
    StripLevel.RENAMED,
    StripLevel.NO_IMPORTS,
    StripLevel.FORMAT_NORMALIZED,
]


def test_detect_eager_fixture() -> None:
    code = (FIXTURES / "eager_pipeline.py").read_text(encoding="utf-8")
    result = detect_eager_lazy(code)
    assert result.method == "eager"
    assert result.evidence["calls_before_first_request"] == 3
    assert result.evidence["calls_during_first_request"] == 0
    assert result.evidence["unrequested_features_computed"] is True
    assert result.evidence["computed_features_before_request"] == [
        "feature_a",
        "feature_b",
        "feature_c",
    ]
    assert result.evidence["trace"] == [
        "feature_a:call",
        "feature_b:call",
        "feature_c:call",
    ]


def test_detect_lazy_fixture() -> None:
    code = (FIXTURES / "lazy_pipeline.py").read_text(encoding="utf-8")
    result = detect_eager_lazy(code)
    assert result.method == "lazy"
    assert result.evidence["calls_before_first_request"] == 0
    assert result.evidence["calls_during_first_request"] == 1
    assert result.evidence["unrequested_features_computed"] is False
    assert result.evidence["computed_features_on_demand"] == ["feature_a"]
    assert result.evidence["trace"] == ["feature_a:call"]


def test_recompute_fixture_is_ambiguous() -> None:
    code = (FIXTURES / "recompute_pipeline.py").read_text(encoding="utf-8")
    result = detect_eager_lazy(code)
    assert result.method == "ambiguous"
    assert result.evidence["reason"] == "recompute_on_repeat_getter"


def test_invalid_fixture_behavioral_fail() -> None:
    tasks = load_eager_lazy_tasks(TASKS_FILE)
    code = (FIXTURES / "invalid_pipeline.py").read_text(encoding="utf-8")
    behavioral = run_eager_lazy_behavioral_oracle(code, tasks[0])
    assert not behavioral.parsed
    result = detect_eager_lazy(code)
    assert result.method == "ambiguous"


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("eager_pipeline.py", "eager"),
        ("lazy_pipeline.py", "lazy"),
    ],
)
def test_survives_all_strip_levels(fixture: str, expected: str) -> None:
    code = (FIXTURES / fixture).read_text(encoding="utf-8")
    for level in STRIP_LEVELS:
        stripped = strip_code(code, level)
        result = detect_eager_lazy(stripped)
        assert result.method == expected, level.value


def test_eager_trace_order_exact() -> None:
    code = (FIXTURES / "eager_pipeline.py").read_text(encoding="utf-8")
    result = detect_eager_lazy(code)
    assert result.evidence["trace"] == [
        "feature_a:call",
        "feature_b:call",
        "feature_c:call",
    ]


def test_lazy_trace_order_exact() -> None:
    code = (FIXTURES / "lazy_pipeline.py").read_text(encoding="utf-8")
    result = detect_eager_lazy(code)
    assert result.evidence["trace"] == ["feature_a:call"]


def test_detect_eager_lazy_file_cli_shape() -> None:
    result = detect_eager_lazy_file(str(FIXTURES / "eager_pipeline.py"))
    payload = result.to_dict()
    assert payload["method"] == "eager"
    assert "evidence" in payload
    assert "calls_before_first_request" in payload["evidence"]
    assert "trace" in payload["evidence"]
    assert "reason" in payload["evidence"]


def test_eager_lazy_pilot_expected_generations() -> None:
    pilot = CoreV2PilotConfig.from_yaml(EAGER_LAZY_CONFIG, project_root())
    items = plan_core_v2_generations(pilot, pilot.load_tasks())
    assert pilot.expected_generations() == 120
    assert len(items) == 120


def test_eager_lazy_prompts_include_operational_definitions() -> None:
    tasks = load_eager_lazy_tasks(TASKS_FILE)
    for task in tasks:
        eager_prompt = build_eager_lazy_generation_prompt(task, "eager")
        lazy_prompt = build_eager_lazy_generation_prompt(task, "lazy")
        assert EAGER_LAZY_METHOD_OPERATIONAL["eager"] in eager_prompt
        assert EAGER_LAZY_METHOD_OPERATIONAL["lazy"] in lazy_prompt
        assert "class FeaturePipeline:" in eager_prompt
        assert "feature_a_fn" in lazy_prompt


@pytest.mark.parametrize("method", ["eager", "lazy"])
def test_eager_lazy_stub_codes_pass_behavioral_oracle(method: str) -> None:
    tasks = load_eager_lazy_tasks(TASKS_FILE)
    for task in tasks:
        code = build_eager_lazy_stub_code(task, method)
        behavioral = run_eager_lazy_behavioral_oracle(code, task)
        assert behavioral.behavioral_pass, task.task_id
        detected = detect_eager_lazy(code, task=task)
        assert detected.method == method, task.task_id


def test_lazy_values_correct_but_eager_timing_is_behaviorally_valid() -> None:
    """Lazy math with eager callback timing: behavioral pass, detector says eager."""
    code = (FIXTURES / "eager_pipeline.py").read_text(encoding="utf-8")
    tasks = load_eager_lazy_tasks(TASKS_FILE)
    behavioral = run_eager_lazy_behavioral_oracle(code, tasks[0])
    assert behavioral.behavioral_pass
    detected = detect_eager_lazy(code, task=tasks[0])
    assert detected.method == "eager"
