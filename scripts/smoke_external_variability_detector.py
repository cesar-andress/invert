#!/usr/bin/env python3
"""Smoke test for external variability detector (not confirmatory evidence)."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from invert_core.external.external_variability_detector import (  # noqa: E402
    ExternalVariabilityProtocol,
    InputBundle,
    analyze_external_variability,
    detector_sha256,
    load_protocol,
    write_freeze_record,
)

FIXTURES = ROOT / "tests" / "external" / "fixtures"
CONFIG = ROOT / "configs" / "external_variability_protocol.yaml"
OUT_DIR = ROOT / "results" / "external_variability"
CSV_PATH = OUT_DIR / "smoke_test_results.csv"
GO_NO_GO_PATH = OUT_DIR / "smoke_go_no_go.json"

BUNDLE = InputBundle(bundle_id="default", args=(4,))


def _expected_validator(case_id: str):
    if case_id == "toy_deterministic":
        return lambda output: output == 8
    if case_id == "toy_randomized":
        return lambda output: isinstance(output, float)
    if case_id == "toy_flaky":
        return lambda output: output == 8
    if case_id == "toy_timeout":
        return lambda output: output == 8
    if case_id == "toy_error":
        return lambda output: output == 8
    raise KeyError(case_id)


def _expected_label(case_id: str) -> str:
    return {
        "toy_deterministic": "stable",
        "toy_randomized": "variable",
        "toy_flaky": "flaky_invalid",
        "toy_timeout": "timeout",
        "toy_error": "error",
    }[case_id]


def _protocol_for_case(case_id: str, base: ExternalVariabilityProtocol) -> ExternalVariabilityProtocol:
    if case_id == "toy_timeout":
        return ExternalVariabilityProtocol(
            run_count=base.run_count,
            timeout_sec=0.05,
            python_hashseed=base.python_hashseed,
            normalize_whitespace=base.normalize_whitespace,
            max_output_chars=base.max_output_chars,
        )
    return base


def main() -> int:
    base_protocol = load_protocol(CONFIG)
    smoke_protocol = ExternalVariabilityProtocol(
        run_count=base_protocol.run_count,
        timeout_sec=base_protocol.timeout_sec,
        python_hashseed=base_protocol.python_hashseed,
        normalize_whitespace=base_protocol.normalize_whitespace,
        max_output_chars=base_protocol.max_output_chars,
    )

    cases = [
        "toy_deterministic",
        "toy_randomized",
        "toy_flaky",
        "toy_timeout",
        "toy_error",
    ]

    rows: list[dict[str, str | int | bool]] = []
    all_pass = True

    for case_id in cases:
        code = (FIXTURES / f"{case_id}.py").read_text(encoding="utf-8")
        protocol = _protocol_for_case(case_id, smoke_protocol)
        validator = _expected_validator(case_id)
        result = analyze_external_variability(
            code,
            artifact_id=case_id,
            entry_point="solve",
            bundles=[BUNDLE],
            protocol=protocol,
            validators={BUNDLE.bundle_id: validator},
        )
        bundle = result.bundle_results[0] if result.bundle_results else None
        observed = result.aggregate_label
        expected = _expected_label(case_id)
        ok = observed == expected
        if not ok:
            all_pass = False
        rows.append(
            {
                "artifact_id": case_id,
                "expected_label": expected,
                "observed_label": observed,
                "externally_valid": result.externally_valid,
                "validation_error": result.validation_error or "",
                "unique_output_hash_count": bundle.unique_output_hash_count if bundle else 0,
                "pass_count": bundle.pass_count if bundle else 0,
                "fail_count": bundle.fail_count if bundle else 0,
                "smoke_pass": ok,
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)

    freeze_path = write_freeze_record()
    sha = detector_sha256()

    go_payload = {
        "study_id": "RQ-EXT-E",
        "recommended": "go" if all_pass else "revise-plan",
        "smoke_tests_passed": all_pass,
        "detector_sha256": sha,
        "detector_frozen": True,
        "freeze_record": str(freeze_path.relative_to(ROOT)),
        "uses_invert_api": False,
        "separate_from_class_e": True,
        "full_external_study_proceed": all_pass,
        "main_blocker": None if all_pass else "smoke_test_mismatch",
        "smoke_csv": str(CSV_PATH.relative_to(ROOT)),
    }
    GO_NO_GO_PATH.write_text(json.dumps(go_payload, indent=2) + "\n", encoding="utf-8")

    print(f"detector_sha256={sha}")
    print(f"smoke_csv={CSV_PATH}")
    print(f"go_no_go={GO_NO_GO_PATH}")
    print(f"freeze_record={freeze_path}")
    for row in rows:
        status = "PASS" if row["smoke_pass"] else "FAIL"
        print(
            f"{status} {row['artifact_id']}: expected={row['expected_label']} "
            f"observed={row['observed_label']}"
        )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
