from __future__ import annotations

from pathlib import Path

import pytest

from invert_external.detectors.output_stability import (
    InputBundle,
    OutputStabilityProtocol,
    analyze_output_stability,
    classify_run_records,
    detector_sha256,
    normalize_output,
    RunRecord,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
BUNDLE = InputBundle(bundle_id="default", args=(4,))
PROTOCOL = OutputStabilityProtocol(run_count=10, timeout_sec=2.0)


def _run(case_id: str, validator, functionally_valid: bool = True):
    code = (FIXTURES / f"{case_id}.py").read_text(encoding="utf-8")
    if case_id == "toy_timeout":
        protocol = OutputStabilityProtocol(run_count=10, timeout_sec=0.05)
    else:
        protocol = PROTOCOL
    return analyze_output_stability(
        code,
        artifact_id=case_id,
        entry_point="solve",
        bundles=[BUNDLE],
        protocol=protocol,
        validators={BUNDLE.bundle_id: validator},
        functionally_valid=functionally_valid,
        validation_error=None if functionally_valid else "fail",
    )


def test_normalize_preserves_order() -> None:
    assert normalize_output([1, 2, 3]) == "[1,2,3]"


def test_classify_stable() -> None:
    records = [RunRecord(0, "pass", True, "a", None), RunRecord(1, "pass", True, "a", None)]
    assert classify_run_records(records, validator_passed=[True, True]) == "stable"


def test_invalid_label() -> None:
    result = _run("toy_deterministic", lambda o: o == 8, functionally_valid=False)
    assert result.label == "invalid"


def test_smoke_deterministic() -> None:
    assert _run("toy_deterministic", lambda o: o == 8).label == "stable"


def test_smoke_randomized() -> None:
    assert _run("toy_randomized", lambda o: isinstance(o, float)).label == "variable"


def test_smoke_flaky() -> None:
    assert _run("toy_flaky", lambda o: o == 8).label == "flaky_invalid"


def test_smoke_timeout() -> None:
    assert _run("toy_timeout", lambda o: o == 8).label == "timeout"


def test_smoke_error_invalid() -> None:
    result = _run("toy_deterministic", lambda o: o == 8, functionally_valid=False)
    assert result.label == "invalid"


def test_sha256_length() -> None:
    assert len(detector_sha256()) == 64
