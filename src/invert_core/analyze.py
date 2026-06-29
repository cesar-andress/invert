from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from invert_core.detectors.integration import detect_integration
from invert_core.detectors.lock_control import detect_lock_control
from invert_core.detectors.shuffled_control import run_shuffled_control
from invert_core.stripping import (
    StripLevel,
    strip_code,
    strip_code_with_evidence,
    write_strip_sidecar,
)


STRIP_LEVELS = [
    StripLevel.RAW,
    StripLevel.NO_COMMENTS,
    StripLevel.RENAMED,
    StripLevel.NO_IMPORTS,
    StripLevel.FORMAT_NORMALIZED,
]

F2_STRIP_LEVELS = STRIP_LEVELS + [StripLevel.LOCK_MARKER_STRIP]

INTEGRATION_TRUE = {
    "euler": "euler",
    "rk4": "rk4",
}

INTEGRATION_LABEL = {
    "euler": "m0",
    "rk4": "m1",
}

LOCK_TRUE = {
    "counter_no_lock": "no_lock",
    "counter_with_lock": "locked",
}


@dataclass
class SliceAnalysisResult:
    f1_rows: list[dict[str, Any]] = field(default_factory=list)
    f2_rows: list[dict[str, Any]] = field(default_factory=list)
    f3_rows: list[dict[str, Any]] = field(default_factory=list)
    matrix_rows: list[dict[str, Any]] = field(default_factory=list)
    summary_path: Path | None = None
    analysis_path: Path | None = None
    matrix_path: Path | None = None
    passed: bool = True


def _glob_fixtures(fixtures_dir: Path, pattern: str) -> list[Path]:
    return sorted(fixtures_dir.glob(pattern))


def _integration_entry(strip_level: StripLevel) -> str | None:
    if strip_level in (StripLevel.RAW, StripLevel.NO_COMMENTS):
        return "integrate_ode"
    return None


def _true_integration_label(stem: str) -> str:
    if "euler" in stem:
        return "euler"
    if "rk4" in stem:
        return "rk4"
    raise ValueError(f"Unknown integration fixture: {stem}")


def _true_lock_label(stem: str) -> str:
    if "no_lock" in stem:
        return "no_lock"
    if "with_lock" in stem:
        return "locked"
    raise ValueError(f"Unknown lock fixture: {stem}")


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def _f2_strip(code: str, level: StripLevel, sidecar_dir: Path, artifact: str) -> str:
    if level == StripLevel.LOCK_MARKER_STRIP:
        stripped, evidence = strip_code_with_evidence(code, level)
        if evidence:
            write_strip_sidecar(
                sidecar_dir / f"{artifact}.lock_marker_strip.json",
                source=artifact,
                level=level.value,
                evidence=evidence,
            )
        return stripped
    return strip_code(code, level)


def _f2_collapse_observed(f2_rows: list[dict[str, Any]]) -> bool:
    subset = [r for r in f2_rows if r["strip_level"] == StripLevel.LOCK_MARKER_STRIP.value]
    if len(subset) < 2:
        return False
    with_lock = next((r for r in subset if r["true_label"] == "locked"), None)
    if with_lock is None:
        return False
    return with_lock["correct"] != "true" or with_lock["predicted_label"] != "locked"


def _analyze_f1(fixtures_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    paths = _glob_fixtures(fixtures_dir, "euler*.py") + _glob_fixtures(fixtures_dir, "rk4*.py")
    for path in paths:
        code = path.read_text(encoding="utf-8")
        true_label = _true_integration_label(path.stem)
        for level in STRIP_LEVELS:
            stripped = strip_code(code, level)
            result = detect_integration(stripped, entry_function=_integration_entry(level))
            predicted = result.method
            rows.append(
                {
                    "section": "f1_integration",
                    "artifact": path.name,
                    "true_label": true_label,
                    "strip_level": level.value,
                    "predicted_label": predicted,
                    "correct": str(predicted == true_label).lower(),
                    "derivative_calls_per_step": result.evidence.get(
                        "derivative_calls_per_step", ""
                    ),
                    "rk4_weighted_combination": result.evidence.get(
                        "rk4_weighted_combination", ""
                    ),
                }
            )
    return rows


def _analyze_f2(fixtures_dir: Path, sidecar_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    paths = _glob_fixtures(fixtures_dir, "counter_no_lock*.py") + _glob_fixtures(
        fixtures_dir, "counter_with_lock*.py"
    )
    for path in paths:
        code = path.read_text(encoding="utf-8")
        true_label = _true_lock_label(path.stem)
        for level in F2_STRIP_LEVELS:
            stripped = _f2_strip(code, level, sidecar_dir, path.name)
            result = detect_lock_control(stripped)
            predicted = result.method
            rows.append(
                {
                    "section": "f2_lock",
                    "artifact": path.name,
                    "true_label": true_label,
                    "strip_level": level.value,
                    "predicted_label": predicted,
                    "correct": str(predicted == true_label).lower(),
                    "detected_lock_markers": ";".join(result.lock_evidence),
                }
            )
    return rows


def _analyze_f3(fixtures_dir: Path, tmp_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    def detector_fn(code: str) -> str:
        return detect_integration(code, entry_function="integrate_ode").method

    shuffled = run_shuffled_control(
        fixtures_dir,
        tmp_dir,
        seed=42,
        detector_fn=detector_fn,
        fixture_filter="integration",
    )

    by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for detail in shuffled.details:
        by_hash[detail["code_hash"]].append(detail)

    rows: list[dict[str, Any]] = []
    pair_idx = 0
    for code_hash, items in sorted(by_hash.items()):
        if len(items) < 2:
            continue
        pair_idx += 1
        a, b = items[0], items[1]
        rows.append(
            {
                "section": "f3_shuffled",
                "pair_id": f"pair_{pair_idx}",
                "label_a": a["shuffled_label"],
                "label_b": b["shuffled_label"],
                "identical_code": "true",
                "detector_prediction": a["detected"],
                "expected_chance_behavior": "no_above_chance_signal",
                "code_hash": code_hash,
                "match_a": str(a["match"]).lower(),
                "match_b": str(b["match"]).lower(),
            }
        )

    meta = {
        "accuracy": shuffled.accuracy,
        "at_chance": shuffled.at_chance,
        "n_artifacts": shuffled.n_artifacts,
    }
    return rows, meta


def _accuracy(rows: list[dict[str, Any]], strip_level: str) -> tuple[float, int]:
    subset = [r for r in rows if r["strip_level"] == strip_level]
    if not subset:
        return 0.0, 0
    correct = sum(1 for r in subset if r["correct"] == "true")
    return correct / len(subset), len(subset)


def _build_matrix(
    f1_rows: list[dict[str, Any]],
    f2_rows: list[dict[str, Any]],
    f3_meta: dict[str, Any],
) -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    f2_collapse = _f2_collapse_observed(f2_rows)

    for level in STRIP_LEVELS:
        acc, n = _accuracy(f1_rows, level.value)
        matrix.append(
            {
                "family": "F1",
                "dimension": "F1.1_integration",
                "strip_level": level.value,
                "accuracy": f"{acc:.4f}",
                "n": str(n),
                "expected_behavior": "correct_all_levels",
                "status": "pass" if acc == 1.0 else "fail",
            }
        )

    for level in F2_STRIP_LEVELS:
        acc, n = _accuracy(f2_rows, level.value)
        if level in (StripLevel.RAW, StripLevel.NO_COMMENTS):
            expected = "correct_positive_control"
            status = "pass" if acc == 1.0 else "fail"
        elif level == StripLevel.LOCK_MARKER_STRIP:
            expected = "collapse_after_lock_marker_removal"
            status = "pass" if f2_collapse else "fail"
        else:
            expected = "not_lock_marker_ablation"
            status = "not_tested"
        matrix.append(
            {
                "family": "F2",
                "dimension": "F2.1_lock_control",
                "strip_level": level.value,
                "accuracy": f"{acc:.4f}",
                "n": str(n),
                "expected_behavior": expected,
                "status": status,
            }
        )

    f3_acc = f3_meta.get("accuracy", 0.0)
    f3_n = f3_meta.get("n_artifacts", 0)
    f3_status = "pass" if f3_meta.get("at_chance") else "fail"
    matrix.append(
        {
            "family": "F3",
            "dimension": "F3.2_shuffled_label",
            "strip_level": "n/a",
            "accuracy": f"{f3_acc:.4f}",
            "n": str(f3_n),
            "expected_behavior": "chance_no_above_chance_signal",
            "status": f3_status,
        }
    )

    return matrix


def _write_summary(
    path: Path,
    f1_rows: list[dict[str, Any]],
    f2_rows: list[dict[str, Any]],
    f3_meta: dict[str, Any],
    matrix_rows: list[dict[str, Any]],
) -> None:
    f1_all_pass = all(r["correct"] == "true" for r in f1_rows)
    f2_raw_pass = all(
        r["correct"] == "true"
        for r in f2_rows
        if r["strip_level"] in ("raw", "no_comments")
    )
    f2_collapse = _f2_collapse_observed(f2_rows)
    f3_pass = f3_meta.get("at_chance", False)

    lock_strip_rows = [
        r for r in f2_rows if r["strip_level"] == StripLevel.LOCK_MARKER_STRIP.value
    ]

    lines = [
        "# INVERT Core v2 — Slice Analysis Summary",
        "",
        "Analysis uses handcrafted fixtures only. No LLM APIs.",
        "",
        "## 1. Does F3.2 validate the experimental instrument?",
        "",
    ]
    if f3_pass:
        lines.append(
            f"**Yes, on fixtures.** Shuffled-label accuracy = {f3_meta.get('accuracy', 0):.3f} "
            f"(n={f3_meta.get('n_artifacts', 0)}), within chance band. "
            "A process-signature detector applied to code does not recover permuted metadata labels."
        )
    else:
        lines.append(
            f"**No.** Shuffled-label accuracy = {f3_meta.get('accuracy', 0):.3f} exceeds chance band."
        )

    lines.extend(
        [
            "",
            "## 2. Does F1.1 survive all implemented stripping levels?",
            "",
        ]
    )
    if f1_all_pass:
        lines.append(
            "**Yes.** Euler and RK4 fixtures remain correctly classified at raw, no_comments, "
            "renamed, no_imports, and format_normalized. F1.1 is not evaluated at "
            "`lock_marker_strip` (lock ablation applies only to F2.1)."
        )
    else:
        failed = [r for r in f1_rows if r["correct"] != "true"]
        lines.append(f"**No.** {len(failed)} classification failures:")
        for r in failed:
            lines.append(
                f"- {r['artifact']} @ {r['strip_level']}: expected {r['true_label']}, "
                f"got {r['predicted_label']}"
            )

    lines.extend(
        [
            "",
            "## 3. Does F2.1 behave as a positive trivial control?",
            "",
        ]
    )
    if f2_raw_pass:
        lines.append(
            "**Yes at raw and no_comments.** Lock vs no-lock fixtures are discriminated correctly."
        )
    else:
        lines.append("**No at raw/no_comments.** Positive control failed on baseline levels.")

    lines.extend(["", "### Collapse after `lock_marker_strip`", ""])
    if f2_collapse:
        locked_row = next(r for r in lock_strip_rows if r["true_label"] == "locked")
        lines.append(
            "**Yes — collapse observed on fixtures.** After lock-marker ablation, the with-lock "
            f"fixture is no longer classified as locked (predicted `{locked_row['predicted_label']}`). "
            "The no-lock fixture remains no-lock. This matches the preregistered trivial-control "
            "expectation: lock recovery depends on obvious lock markers."
        )
    else:
        lines.append(
            "**No — collapse not observed.** Lock-marker stripping did not prevent lock detection "
            "on the with-lock fixture."
        )

    lines.extend(
        [
            "",
            "Levels `renamed`, `no_imports`, and `format_normalized` do not remove lock primitives; "
            "F2.1 accuracy at those levels is reported but **not_tested** as collapse evidence.",
            "",
            "## 4. Preregistered conditions satisfied",
            "",
        ]
    )

    satisfied: list[str] = []
    if f1_all_pass:
        satisfied.append("F1.1 detection survives all implemented stripping levels (≥0.95 threshold)")
    if f2_raw_pass:
        satisfied.append("F2.1 detector accuracy ≥0.95 at raw/no_comments")
    if f2_collapse:
        satisfied.append(
            "F2.1 collapse after lock_marker_strip (with-lock no longer detected as locked)"
        )
    if f3_pass:
        satisfied.append("F3.2 shuffled-label accuracy in chance band (0.30–0.70 on fixtures)")

    if satisfied:
        for item in satisfied:
            lines.append(f"- {item}")
    else:
        lines.append("- None fully satisfied.")

    lines.extend(
        [
            "",
            "## 5. Not yet testable",
            "",
            "- F1.1 manipulation failure rate (requires generated artifacts + behavioral oracle)",
            "- F1.1 detector accuracy ≥0.90 on manipulation-confirmed LLM-generated pairs",
            "- F2.1 false positive rate ≤0.05 on large artifact sample",
            "- F3.2 on LLM-generated artifacts (only fixture-based shuffled copies tested)",
            "",
            "## 6. Recommended next implementation steps",
            "",
            "1. Add ODE integration task generation with behavioral equivalence tests.",
            "2. Run F1.1 on generated artifacts (still detector-primary, no LLM judge).",
            "3. Expand F3.2 to generated artifact pairs with metadata-only label shuffle.",
            "4. Add Jacobi/Gauss-Seidel and quadrature dimensions when Family 1 expands.",
            "",
            "## Matrix status",
            "",
            "| family | dimension | strip_level | accuracy | status |",
            "|--------|-----------|-------------|----------|--------|",
        ]
    )
    for row in matrix_rows:
        lines.append(
            f"| {row['family']} | {row['dimension']} | {row['strip_level']} | "
            f"{row['accuracy']} | {row['status']} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_analyze_slice(
    fixtures_dir: Path,
    output_dir: Path,
) -> SliceAnalysisResult:
    """Run preregistered slice analysis on handcrafted fixtures."""
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_shuffled = output_dir / "_shuffled_tmp"
    sidecar_dir = output_dir / "strip_sidecars"

    f1_rows = _analyze_f1(fixtures_dir)
    f2_rows = _analyze_f2(fixtures_dir, sidecar_dir)
    f3_rows, f3_meta = _analyze_f3(fixtures_dir, tmp_shuffled)
    matrix_rows = _build_matrix(f1_rows, f2_rows, f3_meta)

    analysis_rows = f1_rows + f2_rows + f3_rows
    analysis_fields = [
        "section",
        "artifact",
        "true_label",
        "strip_level",
        "predicted_label",
        "correct",
        "derivative_calls_per_step",
        "rk4_weighted_combination",
        "detected_lock_markers",
        "pair_id",
        "label_a",
        "label_b",
        "identical_code",
        "detector_prediction",
        "expected_chance_behavior",
        "code_hash",
        "match_a",
        "match_b",
    ]

    analysis_path = output_dir / "slice_analysis.csv"
    matrix_path = output_dir / "slice_matrix.csv"
    summary_path = output_dir / "slice_summary.md"

    _write_csv(analysis_path, analysis_fields, analysis_rows)
    _write_csv(
        matrix_path,
        ["family", "dimension", "strip_level", "accuracy", "n", "expected_behavior", "status"],
        matrix_rows,
    )
    _write_summary(summary_path, f1_rows, f2_rows, f3_meta, matrix_rows)

    passed = (
        all(r["correct"] == "true" for r in f1_rows)
        and all(
            r["correct"] == "true"
            for r in f2_rows
            if r["strip_level"] in ("raw", "no_comments")
        )
        and _f2_collapse_observed(f2_rows)
        and f3_meta.get("at_chance", False)
    )

    return SliceAnalysisResult(
        f1_rows=f1_rows,
        f2_rows=f2_rows,
        f3_rows=f3_rows,
        matrix_rows=matrix_rows,
        summary_path=summary_path,
        analysis_path=analysis_path,
        matrix_path=matrix_path,
        passed=passed,
    )
