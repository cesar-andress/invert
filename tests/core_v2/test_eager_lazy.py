from __future__ import annotations

import json
from pathlib import Path

import pytest

from invert_core.detectors.eager_lazy import (
    detect_eager_lazy,
    detect_eager_lazy_file,
    is_genuine_eager,
    is_genuine_lazy,
    pole_manipulation_success,
)
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
        stripped = strip_code(code, level, dimension="eager_vs_lazy")
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


def test_genuine_pole_flags_on_fixtures() -> None:
    eager = detect_eager_lazy((FIXTURES / "eager_pipeline.py").read_text(encoding="utf-8"))
    lazy = detect_eager_lazy((FIXTURES / "lazy_pipeline.py").read_text(encoding="utf-8"))
    assert is_genuine_eager(eager.evidence)
    assert pole_manipulation_success("eager", eager.evidence)
    assert not is_genuine_lazy(eager.evidence)
    assert is_genuine_lazy(lazy.evidence)
    assert pole_manipulation_success("lazy", lazy.evidence)
    assert not is_genuine_eager(lazy.evidence)


def test_full_demand_control_lazy_becomes_ambiguous() -> None:
    code = (FIXTURES / "lazy_pipeline.py").read_text(encoding="utf-8")
    result = detect_eager_lazy(code, demand_pattern="full")
    assert result.method == "ambiguous"
    assert result.evidence["reason"] == "full_demand_no_avoidable_computation_remaining"
    assert result.evidence["demand_pattern"] == "full"
    assert len(result.evidence["trace"]) == 3


def test_full_demand_control_eager_still_recoverable() -> None:
    code = (FIXTURES / "eager_pipeline.py").read_text(encoding="utf-8")
    result = detect_eager_lazy(code, demand_pattern="full")
    assert result.method == "eager"
    assert result.evidence["calls_before_first_request"] == 3
    assert result.evidence["calls_during_first_request"] == 0


def test_full_demand_control_recovery_drops_for_lazy_stub() -> None:
    tasks = load_eager_lazy_tasks(TASKS_FILE)
    task = tasks[0]
    lazy_code = build_eager_lazy_stub_code(task, "lazy")
    partial = detect_eager_lazy(lazy_code, task=task, demand_pattern="partial")
    full = detect_eager_lazy(lazy_code, task=task, demand_pattern="full")
    assert partial.method == "lazy"
    assert full.method == "ambiguous"


def test_analyze_run_control_aggregation(tmp_path: Path) -> None:
    from invert_core.analyze_eager_lazy_run import _accuracy, _manipulation_rate, _row_from_detection
    from invert_core.detectors.eager_lazy import detect_eager_lazy as detect

    art = {
        "model": "local_stub",
        "task_id": "small_positive_vector",
        "method": "lazy",
        "rep": 1,
    }
    code = (FIXTURES / "lazy_pipeline.py").read_text(encoding="utf-8")
    partial = detect(code, demand_pattern="partial")
    full = detect(code, demand_pattern="full")
    rows = [
        _row_from_detection(
            run_name="test",
            art=art,
            strip_level="raw",
            parsed=True,
            behavioral_pass=True,
            valid_artifact=True,
            result=partial,
            include_manipulation=True,
        ),
        _row_from_detection(
            run_name="test",
            art={**art, "method": "eager"},
            strip_level="raw",
            parsed=True,
            behavioral_pass=True,
            valid_artifact=True,
            result=detect((FIXTURES / "eager_pipeline.py").read_text(encoding="utf-8")),
            include_manipulation=True,
        ),
    ]
    full_rows = [
        _row_from_detection(
            run_name="test",
            art=art,
            strip_level="raw",
            parsed=True,
            behavioral_pass=True,
            valid_artifact=True,
            result=full,
            include_manipulation=False,
        ),
    ]
    assert _manipulation_rate(rows, requested_method="lazy") == 1.0
    assert _accuracy(rows) == 1.0
    assert _accuracy(full_rows) == 0.0

