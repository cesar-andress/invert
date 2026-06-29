from __future__ import annotations

import json
from pathlib import Path

import pytest

from invert_core.detectors.integration import detect_integration
from invert_core.detectors.lock_control import detect_lock_control
from invert_core.stripping import (
    LOCK_MARKER_PLACEHOLDER,
    StripLevel,
    lock_marker_strip,
    strip_code,
    strip_code_with_evidence,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def with_lock_code() -> str:
    return (FIXTURES / "counter_with_lock.py").read_text(encoding="utf-8")


@pytest.fixture
def no_lock_code() -> str:
    return (FIXTURES / "counter_no_lock.py").read_text(encoding="utf-8")


@pytest.fixture
def euler_code() -> str:
    return (FIXTURES / "euler_m0.py").read_text(encoding="utf-8")


@pytest.fixture
def rk4_code() -> str:
    return (FIXTURES / "rk4_m1.py").read_text(encoding="utf-8")


def test_lock_markers_removed_from_with_lock_fixture(with_lock_code: str) -> None:
    stripped, evidence = lock_marker_strip(with_lock_code)

    assert "threading" not in stripped
    assert "Lock()" not in stripped
    assert "with _lock" not in stripped
    assert LOCK_MARKER_PLACEHOLDER in stripped
    assert evidence.markers_removed
    assert evidence.replacements_made >= 1


def test_no_lock_fixture_remains_no_lock(no_lock_code: str) -> None:
    stripped, _ = lock_marker_strip(no_lock_code)
    result = detect_lock_control(stripped)
    assert result.method == "no_lock"
    assert not result.has_lock


def test_lock_detector_not_confident_after_lock_marker_strip(with_lock_code: str) -> None:
    stripped, _ = lock_marker_strip(with_lock_code)
    result = detect_lock_control(stripped)
    assert result.method == "no_lock"
    assert not result.has_lock


def test_integration_detector_survives_lock_marker_strip(
    euler_code: str, rk4_code: str
) -> None:
    for code, expected in ((euler_code, "euler"), (rk4_code, "rk4")):
        stripped = strip_code(code, StripLevel.LOCK_MARKER_STRIP)
        result = detect_integration(stripped, entry_function="integrate_ode")
        assert result.method == expected


def test_strip_cli_level_supports_lock_marker_strip(with_lock_code: str) -> None:
    stripped, evidence = strip_code_with_evidence(with_lock_code, StripLevel.LOCK_MARKER_STRIP)
    assert evidence is not None
    assert "markers_removed" in evidence
    assert isinstance(evidence["markers_removed"], list)


def test_sidecar_payload_shape(with_lock_code: str, tmp_path: Path) -> None:
    from invert_core.stripping import write_strip_sidecar

    _, evidence = strip_code_with_evidence(with_lock_code, StripLevel.LOCK_MARKER_STRIP)
    assert evidence is not None
    sidecar = tmp_path / "counter.sidecar.json"
    write_strip_sidecar(
        sidecar,
        source="counter_with_lock.py",
        level=StripLevel.LOCK_MARKER_STRIP.value,
        evidence=evidence,
    )
    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    assert payload["level"] == "lock_marker_strip"
    assert payload["replacements_made"] >= 1
