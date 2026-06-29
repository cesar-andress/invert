from __future__ import annotations

import csv
from pathlib import Path

import pytest

from invert_core.summarize_core_v2 import (
    DIMENSION_SUMMARY_FIELDS,
    MODEL_SUMMARY_FIELDS,
    run_summarize_core_v2,
)
from invert_core.tasks import project_root


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_summarize_core_v2_synthetic_runs(tmp_path: Path) -> None:
    runs_root = tmp_path / "results" / "core_v2" / "runs"
    run_dir = runs_root / "test_euler_run"
    run_dir.mkdir(parents=True)

    (run_dir / "metadata.json").write_text(
        '{"run_name":"test_euler_run","dimension":"euler_vs_rk4"}',
        encoding="utf-8",
    )

    summary_fields = [
        "model",
        "task_id",
        "method",
        "strip_level",
        "all_generated_n",
        "all_generated_detector_accuracy",
        "all_generated_behavioral_pass_rate",
        "all_generated_ambiguous_rate",
    ]
    valid_fields = [
        "model",
        "task_id",
        "method",
        "strip_level",
        "valid_n",
        "valid_detector_accuracy",
        "valid_ambiguous_rate",
    ]

    _write_csv(
        run_dir / "integration_summary.csv",
        summary_fields,
        [
            {
                "model": "model_a",
                "task_id": "t1",
                "method": "euler",
                "strip_level": "raw",
                "all_generated_n": "6",
                "all_generated_detector_accuracy": "1.0000",
                "all_generated_behavioral_pass_rate": "1.0000",
                "all_generated_ambiguous_rate": "0.0000",
            },
            {
                "model": "model_a",
                "task_id": "t1",
                "method": "rk4",
                "strip_level": "raw",
                "all_generated_n": "6",
                "all_generated_detector_accuracy": "1.0000",
                "all_generated_behavioral_pass_rate": "1.0000",
                "all_generated_ambiguous_rate": "0.0000",
            },
            {
                "model": "model_b",
                "task_id": "t1",
                "method": "euler",
                "strip_level": "raw",
                "all_generated_n": "6",
                "all_generated_detector_accuracy": "1.0000",
                "all_generated_behavioral_pass_rate": "0.5000",
                "all_generated_ambiguous_rate": "0.0000",
            },
        ],
    )
    _write_csv(
        run_dir / "integration_valid_only_summary.csv",
        valid_fields,
        [
            {
                "model": "model_a",
                "task_id": "t1",
                "method": "euler",
                "strip_level": "raw",
                "valid_n": "6",
                "valid_detector_accuracy": "1.0000",
                "valid_ambiguous_rate": "0.0000",
            },
            {
                "model": "model_a",
                "task_id": "t1",
                "method": "rk4",
                "strip_level": "raw",
                "valid_n": "6",
                "valid_detector_accuracy": "1.0000",
                "valid_ambiguous_rate": "0.0000",
            },
            {
                "model": "model_a",
                "task_id": "t1",
                "method": "euler",
                "strip_level": "format_normalized",
                "valid_n": "6",
                "valid_detector_accuracy": "1.0000",
                "valid_ambiguous_rate": "0.0000",
            },
            {
                "model": "model_a",
                "task_id": "t1",
                "method": "rk4",
                "strip_level": "format_normalized",
                "valid_n": "6",
                "valid_detector_accuracy": "1.0000",
                "valid_ambiguous_rate": "0.0000",
            },
            {
                "model": "model_b",
                "task_id": "t1",
                "method": "euler",
                "strip_level": "raw",
                "valid_n": "3",
                "valid_detector_accuracy": "1.0000",
                "valid_ambiguous_rate": "0.0000",
            },
        ],
    )

    result = run_summarize_core_v2(tmp_path)
    assert result.model_summary_path.exists()
    assert result.dimension_summary_path.exists()
    assert result.decision_report_path.exists()

    model_a = next(r for r in result.model_rows if r["model"] == "model_a")
    assert model_a["valid_n"] == "12"
    assert model_a["survives_preregistered_rule"] == "true"
    assert model_a["failure_reason"] == ""

    model_b = next(r for r in result.model_rows if r["model"] == "model_b")
    assert model_b["failure_reason"] == "invalid_generation"

    euler_dim = next(r for r in result.dimension_rows if r["dimension"] == "euler_vs_rk4")
    assert euler_dim["runs_found"] == "1"
    assert euler_dim["models_survived"] == "1"
    assert euler_dim["status"] == "promising_if_1_model_survives"

    quad_dim = next(
        r for r in result.dimension_rows if r["dimension"] == "trapezoidal_vs_simpson"
    )
    assert quad_dim["status"] == "insufficient_data"

    eager_dim = next(r for r in result.dimension_rows if r["dimension"] == "eager_vs_lazy")
    assert eager_dim["status"] == "insufficient_data"

    report = result.decision_report_path.read_text(encoding="utf-8")
    assert "Class B not yet evaluated." in report
    assert "Class C not yet evaluated." in report
    assert "Class D not yet evaluated." in report
    assert "Class C: dynamic temporal / avoidable-computation signatures" in report
    assert "Class D: dynamic order process signatures" in report


def test_summarize_core_v2_real_runs_if_present() -> None:
    root = project_root()
    runs_root = root / "results" / "core_v2" / "runs"
    if not (runs_root / "core_v2_euler_rk4_pilot_local_001" / "integration_summary.csv").exists():
        pytest.skip("local euler pilot summaries not present")

    result = run_summarize_core_v2(root)
    assert result.model_rows
    assert len(result.dimension_rows) == 5

    for path in (
        result.model_summary_path,
        result.dimension_summary_path,
        result.decision_report_path,
    ):
        assert path.exists()

    with open(result.model_summary_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == MODEL_SUMMARY_FIELDS

    with open(result.dimension_summary_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == DIMENSION_SUMMARY_FIELDS
