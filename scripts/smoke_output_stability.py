#!/usr/bin/env python3
"""Smoke tests for invert_external output-stability detector."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("PYTHONHASHSEED", "0")

from invert_external.detectors.output_stability import (  # noqa: E402
    InputBundle,
    OutputStabilityProtocol,
    analyze_output_stability,
    detector_sha256,
    write_freeze_record,
    write_sha256_file,
)

FIXTURES = ROOT / "tests" / "invert_external" / "fixtures"
OUT = ROOT / "external_variability_smoke_results.csv"
BUNDLE = InputBundle(bundle_id="default", args=(4,))


def _expected(case_id: str) -> str:
    return {
        "toy_deterministic": "stable",
        "toy_randomized": "variable",
        "toy_flaky": "flaky_invalid",
        "toy_timeout": "timeout",
        "toy_error": "invalid",
    }[case_id]


def _validator(case_id: str):
    if case_id == "toy_randomized":
        return lambda o: isinstance(o, float)
    return lambda o: o == 8


def main() -> int:
    protocol = OutputStabilityProtocol(run_count=10, timeout_sec=2.0)
    rows = []
    ok = True
    for case_id in [
        "toy_deterministic",
        "toy_randomized",
        "toy_flaky",
        "toy_timeout",
        "toy_error",
    ]:
        code = (FIXTURES / f"{case_id}.py").read_text(encoding="utf-8")
        proto = protocol
        if case_id == "toy_timeout":
            proto = OutputStabilityProtocol(run_count=10, timeout_sec=0.05)
        valid = case_id != "toy_error"
        result = analyze_output_stability(
            code,
            artifact_id=case_id,
            entry_point="solve",
            bundles=[BUNDLE],
            protocol=proto,
            validators={BUNDLE.bundle_id: _validator(case_id)},
            functionally_valid=valid,
            validation_error=None if valid else "functional_fail",
        )
        expected = _expected(case_id)
        passed = result.label == expected
        ok = ok and passed
        rows.append(
            {
                "case_id": case_id,
                "expected": expected,
                "observed": result.label,
                "pass": passed,
            }
        )

    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    sha = detector_sha256()
    write_sha256_file()
    write_freeze_record()
    print(f"sha256={sha}")
    print(f"smoke_csv={OUT}")
    for row in rows:
        print(f"{'PASS' if row['pass'] else 'FAIL'} {row['case_id']}: {row['observed']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
