from __future__ import annotations

from pathlib import Path

import pytest

from invert_core.detectors.quadrature import detect_quadrature
from invert_core.stripping import StripLevel, strip_code

FIXTURES = Path(__file__).resolve().parent / "fixtures"

FAMILY_FIXTURES = [
    "trap_family_a.py",
    "trap_family_b.py",
    "trap_family_c.py",
    "trap_family_d.py",
    "trap_family_e.py",
    "trap_family_f.py",
    "trap_family_g.py",
]

STRIP_LEVELS = [
    StripLevel.RAW,
    StripLevel.RENAMED,
    StripLevel.NO_IMPORTS,
    StripLevel.FORMAT_NORMALIZED,
]


def _entry_for_level(level: StripLevel) -> str | None:
    if level == StripLevel.RAW:
        return "integrate"
    return None


@pytest.mark.parametrize("fixture_name", FAMILY_FIXTURES)
@pytest.mark.parametrize("level", STRIP_LEVELS)
def test_trap_family_detected_after_stripping(fixture_name: str, level: StripLevel) -> None:
    code = (FIXTURES / fixture_name).read_text(encoding="utf-8")
    stripped = strip_code(code, level)
    result = detect_quadrature(stripped, entry_function=_entry_for_level(level))
    assert result.method == "trapezoidal", f"{fixture_name} @ {level.value}: {result.evidence}"


@pytest.mark.parametrize(
    "fixture_name",
    ["trap_counter_midpoint.py", "trap_counter_simpson_like.py", "quadrature_ambiguous.py"],
)
@pytest.mark.parametrize("level", STRIP_LEVELS)
def test_trap_counterexamples_not_trapezoidal(fixture_name: str, level: StripLevel) -> None:
    code = (FIXTURES / fixture_name).read_text(encoding="utf-8")
    stripped = strip_code(code, level)
    result = detect_quadrature(stripped, entry_function=_entry_for_level(level))
    assert result.method != "trapezoidal", f"{fixture_name} @ {level.value}"
