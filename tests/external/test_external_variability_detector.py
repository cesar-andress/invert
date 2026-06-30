from __future__ import annotations

from pathlib import Path

import pytest

from invert_core.external.external_variability_detector import (
    ExternalVariabilityProtocol,
    InputBundle,
    RunRecord,
    analyze_external_variability,
    classify_run_records,
    detector_sha256,
    hash_normalized_output,
    normalize_output,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
BUNDLE = InputBundle(bundle_id="default", args=(4,))
PROTOCOL = ExternalVariabilityProtocol(run_count=10, timeout_sec=2.0)


def _analyze(case_id: str, validator):
    code = (FIXTURES / f"{case_id}.py").read_text(encoding="utf-8")
    protocol = PROTOCOL
    if case_id == "toy_timeout":
        protocol = ExternalVariabilityProtocol(run_count=10, timeout_sec=0.05)
    return analyze_external_variability(
        code,
        artifact_id=case_id,
        entry_point="solve",
        bundles=[BUNDLE],
        protocol=protocol,
        validators={BUNDLE.bundle_id: validator},
    )


def test_normalize_output_preserves_list_order() -> None:
    assert normalize_output([1, 2, 3]) == "[1,2,3]"
    assert normalize_output([3, 2, 1]) == "[3,2,1]"


def test_normalize_output_set_without_sort_flag_is_ambiguous() -> None:
    assert normalize_output({1, 2}) is None


def test_classify_stable() -> None:
    records = [
        RunRecord(0, "pass", True, "abc", None),
        RunRecord(1, "pass", True, "abc", None),
    ]
    assert classify_run_records(records, validator_passed=[True, True]) == "stable"


def test_classify_variable() -> None:
    records = [
        RunRecord(0, "pass", True, "abc", None),
        RunRecord(1, "pass", True, "def", None),
    ]
    assert classify_run_records(records, validator_passed=[True, True]) == "variable"


def test_classify_flaky_invalid() -> None:
    records = [
        RunRecord(0, "pass", True, "abc", None),
        RunRecord(1, "pass", True, "def", None),
    ]
    assert classify_run_records(records, validator_passed=[True, False]) == "flaky_invalid"


def test_classify_ambiguous() -> None:
    records = [
        RunRecord(0, "ambiguous", False, None, "output_normalization_failed"),
        RunRecord(1, "pass", True, "abc", None),
    ]
    assert classify_run_records(records, validator_passed=[False, True]) == "ambiguous"


def test_detector_sha256_is_stable() -> None:
    assert len(detector_sha256()) == 64


def test_smoke_deterministic_stable() -> None:
    result = _analyze("toy_deterministic", lambda output: output == 8)
    assert result.aggregate_label == "stable"


def test_smoke_randomized_variable() -> None:
    result = _analyze("toy_randomized", lambda output: isinstance(output, float))
    assert result.aggregate_label == "variable"


def test_smoke_flaky_invalid() -> None:
    result = _analyze("toy_flaky", lambda output: output == 8)
    assert result.aggregate_label == "flaky_invalid"


def test_smoke_timeout() -> None:
    result = _analyze("toy_timeout", lambda output: output == 8)
    assert result.aggregate_label == "timeout"


def test_smoke_error() -> None:
    result = _analyze("toy_error", lambda output: output == 8)
    assert result.validation_passed is False
    assert result.aggregate_label == "error"
