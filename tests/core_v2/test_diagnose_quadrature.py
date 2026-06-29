from __future__ import annotations

import csv
from pathlib import Path

import pytest

from invert_core.diagnose_quadrature import (
    DIAGNOSIS_FIELDS,
    analyze_trapezoidal_code_patterns,
    classify_trapezoidal_failure,
    run_diagnose_quadrature,
)
from invert_core.tasks import project_root

COMBINED_ENDPOINT = '''
def integrate(f, a, b, n):
    h = (b - a) / n
    s = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        s += f(a + i * h)
    return s * h
'''

LATE_H_SCALE = '''
def integrate(f, a, b, n):
    h = (b - a) / n
    result = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        result += f(a + i * h)
    result *= h
    return result
'''

SIMPSON_BODY = '''
def integrate(f, a, b, n):
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        x = a + i * h
        if i % 2 == 1:
            s += 4 * f(x)
        else:
            s += 2 * f(x)
    return s * h / 3
'''


def test_analyze_combined_endpoint_pattern() -> None:
    patterns = analyze_trapezoidal_code_patterns(COMBINED_ENDPOINT, entry_function="integrate")
    assert patterns["has_endpoint_averaging"]
    assert patterns["has_h_times_pattern"]
    assert patterns["has_loop_accumulation"]


def test_classify_detector_too_strict_for_combined_endpoint() -> None:
    patterns = analyze_trapezoidal_code_patterns(COMBINED_ENDPOINT, entry_function="integrate")
    cls, _ = classify_trapezoidal_failure(
        strip_level="raw",
        detected_method="ambiguous",
        behavioral_pass=True,
        patterns=patterns,
        detections_by_level={"raw": "ambiguous"},
        code=COMBINED_ENDPOINT,
        entry_function="integrate",
    )
    assert cls == "detector_too_strict"


def test_classify_nonstandard_for_late_h_scale() -> None:
    patterns = analyze_trapezoidal_code_patterns(LATE_H_SCALE, entry_function="integrate")
    cls, _ = classify_trapezoidal_failure(
        strip_level="raw",
        detected_method="ambiguous",
        behavioral_pass=True,
        patterns=patterns,
        detections_by_level={"raw": "ambiguous"},
        code=LATE_H_SCALE,
        entry_function="integrate",
    )
    assert cls in {"detector_too_strict", "nonstandard_valid_trapezoidal"}


def test_classify_not_trapezoidal_for_simpson_body() -> None:
    patterns = analyze_trapezoidal_code_patterns(SIMPSON_BODY, entry_function="integrate")
    cls, _ = classify_trapezoidal_failure(
        strip_level="raw",
        detected_method="simpson",
        behavioral_pass=False,
        patterns=patterns,
        detections_by_level={"raw": "simpson"},
        code=SIMPSON_BODY,
        entry_function="integrate",
    )
    assert cls == "not_trapezoidal"


def test_classify_stripping_regression() -> None:
    renamed = '''
def x0(x1, x2, x3, x4):
    x5 = (x3 - x2) / x4
    x6 = 0.5 * (x1(x2) + x1(x3))
    for x7 in x8(1, x4):
        x6 += x1(x2 + x7 * x5)
    return x6 * x5
'''
    patterns = analyze_trapezoidal_code_patterns(renamed, entry_function=None)
    cls, _ = classify_trapezoidal_failure(
        strip_level="renamed",
        detected_method="ambiguous",
        behavioral_pass=True,
        patterns=patterns,
        detections_by_level={"raw": "ambiguous", "renamed": "ambiguous"},
        code=renamed,
        entry_function=None,
    )
    assert cls == "stripping_broke_detector"


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_run_diagnose_quadrature_synthetic(tmp_path: Path) -> None:
    run_name = "test_quad_diag"
    data_root = tmp_path / "data" / "core_v2"
    results_dir = tmp_path / "results" / "core_v2" / "runs" / run_name
    code_path = (
        data_root
        / "code"
        / run_name
        / "model_a"
        / "integrate_sin_0_pi"
        / "trapezoidal"
        / "rep_1.py"
    )
    code_path.parent.mkdir(parents=True, exist_ok=True)
    code_path.write_text(COMBINED_ENDPOINT, encoding="utf-8")

    detection_fields = [
        "run",
        "model",
        "task_id",
        "method",
        "rep",
        "strip_level",
        "parsed",
        "behavioral_pass",
        "valid_artifact",
        "detected_method",
        "detector_correct",
        "ambiguous",
        "has_endpoint_half_weights",
        "has_simpson_4_2_pattern",
        "coefficient_literals",
        "function_eval_pattern",
    ]
    _write_csv(
        results_dir / "quadrature_detection.csv",
        detection_fields,
        [
            {
                "run": run_name,
                "model": "model_a",
                "task_id": "integrate_sin_0_pi",
                "method": "trapezoidal",
                "rep": "1",
                "strip_level": "raw",
                "parsed": "true",
                "behavioral_pass": "true",
                "valid_artifact": "true",
                "detected_method": "ambiguous",
                "detector_correct": "false",
                "ambiguous": "true",
                "has_endpoint_half_weights": "false",
                "has_simpson_4_2_pattern": "false",
                "coefficient_literals": "0.5;1.0",
                "function_eval_pattern": "loop_weighted_sum",
            }
        ],
    )

    result = run_diagnose_quadrature(run_name, tmp_path)
    assert result.csv_path.exists()
    assert result.md_path.exists()
    assert len(result.rows) == 1
    assert result.rows[0]["failure_classification"] == "detector_too_strict"

    with open(result.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == DIAGNOSIS_FIELDS


def test_run_diagnose_quadrature_real_run_if_present() -> None:
    root = project_root()
    run = "core_v2_quadrature_pilot_local_001"
    detection = root / "results" / "core_v2" / "runs" / run / "quadrature_detection.csv"
    if not detection.exists():
        pytest.skip("quadrature detection csv not present")

    result = run_diagnose_quadrature(run, root)
    assert result.csv_path.exists()
    assert result.md_path.exists()
