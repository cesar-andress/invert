from __future__ import annotations

from pathlib import Path

from invert_core.analyze import run_analyze_slice
from invert_core.tasks import fixtures_dir


def test_analyze_slice_passes(tmp_path: Path) -> None:
    result = run_analyze_slice(fixtures_dir(), tmp_path)
    assert result.analysis_path.exists()
    assert result.matrix_path.exists()
    assert result.summary_path.exists()
    assert result.passed
    assert len(result.f1_rows) == 10  # 2 fixtures x 5 strip levels
    assert len(result.f2_rows) == 12  # 2 fixtures x 6 strip levels
    assert len(result.f3_rows) >= 2
