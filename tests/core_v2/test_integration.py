from __future__ import annotations

from pathlib import Path

import pytest

from invert_core.detectors.integration import detect_integration
from invert_core.detectors.lock_control import detect_lock_control
from invert_core.detectors.shuffled_control import run_shuffled_control
from invert_core.stripping import StripLevel, strip_code

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def euler_code() -> str:
    return (FIXTURES / "euler_m0.py").read_text(encoding="utf-8")


@pytest.fixture
def rk4_code() -> str:
    return (FIXTURES / "rk4_m1.py").read_text(encoding="utf-8")


def test_detect_euler(euler_code: str) -> None:
    result = detect_integration(euler_code, entry_function="integrate_ode")
    assert result.method == "euler"
    assert result.evidence["derivative_calls_per_step"] == 1
    assert result.evidence["rk4_weighted_combination"] is False


def test_detect_rk4(rk4_code: str) -> None:
    result = detect_integration(rk4_code, entry_function="integrate_ode")
    assert result.method == "rk4"
    assert result.evidence["derivative_calls_per_step"] >= 4
    assert result.evidence["rk4_weighted_combination"] is True


@pytest.mark.parametrize(
    "level",
    [
        StripLevel.NO_COMMENTS,
        StripLevel.RENAMED,
        StripLevel.NO_IMPORTS,
        StripLevel.FORMAT_NORMALIZED,
    ],
)
def test_euler_survives_stripping(euler_code: str, level: StripLevel) -> None:
    stripped = strip_code(euler_code, level)
    ef = "integrate_ode" if level in (StripLevel.RAW, StripLevel.NO_COMMENTS) else None
    result = detect_integration(stripped, entry_function=ef)
    assert result.method == "euler"


@pytest.mark.parametrize(
    "level",
    [
        StripLevel.NO_COMMENTS,
        StripLevel.RENAMED,
        StripLevel.NO_IMPORTS,
        StripLevel.FORMAT_NORMALIZED,
    ],
)
def test_rk4_survives_stripping(rk4_code: str, level: StripLevel) -> None:
    stripped = strip_code(rk4_code, level)
    ef = "integrate_ode" if level in (StripLevel.RAW, StripLevel.NO_COMMENTS) else None
    result = detect_integration(stripped, entry_function=ef)
    assert result.method == "rk4"


def test_lock_no_lock() -> None:
    code = (FIXTURES / "counter_no_lock.py").read_text(encoding="utf-8")
    result = detect_lock_control(code)
    assert result.method == "no_lock"
    assert not result.has_lock


def test_lock_with_lock() -> None:
    code = (FIXTURES / "counter_with_lock.py").read_text(encoding="utf-8")
    result = detect_lock_control(code)
    assert result.method == "locked"
    assert result.has_lock


def test_f3_shuffled_at_chance(tmp_path: Path) -> None:
    from invert_core.detectors.integration import detect_integration

    def detector_fn(code: str) -> str:
        return detect_integration(code, entry_function="integrate_ode").method

    result = run_shuffled_control(
        FIXTURES, tmp_path, seed=42, detector_fn=detector_fn, fixture_filter="integration"
    )
    assert result.n_artifacts >= 8
    assert result.at_chance
    assert 0.30 <= result.accuracy <= 0.70
