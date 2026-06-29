from __future__ import annotations

import csv
from pathlib import Path

import pytest

from invert_core.audit_eager_lazy_pole_asymmetry import (
    FROZEN_EAGER_LAZY_RUN,
    POLE_ASYMMETRY_FIELDS,
    run_eager_lazy_pole_asymmetry_audit,
)
from invert_core.tasks import project_root


def test_run_pole_asymmetry_audit_real_run_if_present() -> None:
    root = project_root()
    run_dir = root / "results" / "core_v2" / "runs" / FROZEN_EAGER_LAZY_RUN
    if not (run_dir / "eager_lazy_detection.csv").exists():
        pytest.skip("frozen eager/lazy detection CSV not present")

    result = run_eager_lazy_pole_asymmetry_audit(FROZEN_EAGER_LAZY_RUN, root)
    assert result is not None
    assert result.csv_path is not None
    assert result.md_path is not None
    assert result.csv_path.exists()
    assert result.md_path.exists()
    assert len(result.rows) == 4

    with open(result.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == POLE_ASYMMETRY_FIELDS
        rows = list(reader)

    partial = [r for r in rows if r["section"] == "partial_demand"]
    full = [r for r in rows if r["section"] == "full_demand_control"]
    assert {r["pole"] for r in partial} == {"eager", "lazy"}
    assert {r["pole"] for r in full} == {"eager", "lazy"}

    eager = next(r for r in partial if r["pole"] == "eager")
    lazy = next(r for r in partial if r["pole"] == "lazy")
    assert eager["detector_accuracy_raw"] == "1.0000"
    assert lazy["detector_accuracy_raw"] == "1.0000"
    assert lazy["detector_accuracy_format_normalized"] == "0.7500"

    lazy_full = next(r for r in full if r["pole"] == "lazy")
    assert lazy_full["full_demand_ambiguous_rate"] == "1.0000"

    md = result.md_path.read_text(encoding="utf-8")
    assert "Does partial-demand recovery hold for both poles?" in md
    assert "Does lazy collapse under full demand?" in md
    assert result.answers["conservative_phrasing"]


def test_summarize_includes_class_c_asymmetry_note() -> None:
    root = project_root()
    run_dir = root / "results" / "core_v2" / "runs" / FROZEN_EAGER_LAZY_RUN
    if not (run_dir / "eager_lazy_detection.csv").exists():
        pytest.skip("frozen eager/lazy detection CSV not present")

    from invert_core.summarize_core_v2 import run_summarize_core_v2

    result = run_summarize_core_v2(root)
    report = result.decision_report_path.read_text(encoding="utf-8")
    assert "## 8.1 Class C pole asymmetry (frozen generalization audit)" in report
    assert "eager_lazy_pole_asymmetry.md" in report
