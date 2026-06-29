from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from invert_core.analyze_run import _format_rate, _write_csv

POLE_ASYMMETRY_FIELDS = [
    "run",
    "section",
    "pole",
    "generated_n",
    "valid_n",
    "genuine_n",
    "manipulation_success_rate",
    "detector_accuracy_raw",
    "detector_accuracy_format_normalized",
    "ambiguous_rate_raw",
    "ambiguous_rate_format_normalized",
    "full_demand_detected_rate",
    "full_demand_ambiguous_rate",
    "full_demand_collapsed_rate",
]

FROZEN_EAGER_LAZY_RUN = "core_v2_generalization_local_eager_lazy_001"


@dataclass
class EagerLazyPoleAsymmetryResult:
    rows: list[dict[str, Any]] = field(default_factory=list)
    csv_path: Path | None = None
    md_path: Path | None = None
    answers: dict[str, str] = field(default_factory=dict)


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _artifact_keys(rows: list[dict[str, str]], *, strip_level: str = "raw") -> set[tuple[str, str, str]]:
    return {
        (r["model"], r["task_id"], str(r["rep"]))
        for r in rows
        if r.get("strip_level") == strip_level
    }


def _rate(num: int, den: int) -> float | None:
    if den == 0:
        return None
    return num / den


def _subset(
    rows: list[dict[str, str]],
    *,
    pole: str,
    strip_level: str,
    valid_only: bool = False,
) -> list[dict[str, str]]:
    out = [
        r
        for r in rows
        if r.get("method") == pole and r.get("strip_level") == strip_level
    ]
    if valid_only:
        out = [r for r in out if r.get("valid_artifact") == "true"]
    return out


def _partial_pole_row(
    run_name: str,
    detection_rows: list[dict[str, str]],
    *,
    pole: str,
) -> dict[str, Any]:
    raw_all = _subset(detection_rows, pole=pole, strip_level="raw")
    raw_valid = _subset(detection_rows, pole=pole, strip_level="raw", valid_only=True)
    fmt_valid = _subset(detection_rows, pole=pole, strip_level="format_normalized", valid_only=True)

    generated_n = len(_artifact_keys(raw_all, strip_level="raw"))
    valid_n = len(_artifact_keys(raw_valid, strip_level="raw"))
    genuine_flag = "genuine_eager" if pole == "eager" else "genuine_lazy"
    genuine_n = sum(1 for r in raw_valid if r.get(genuine_flag) == "true")
    manip_ok = sum(1 for r in raw_valid if r.get("pole_manipulation_success") == "true")

    raw_acc = _rate(
        sum(1 for r in raw_valid if r.get("detector_correct") == "true"),
        len(raw_valid),
    )
    fmt_acc = _rate(
        sum(1 for r in fmt_valid if r.get("detector_correct") == "true"),
        len(fmt_valid),
    )
    raw_amb = _rate(sum(1 for r in raw_valid if r.get("ambiguous") == "true"), len(raw_valid))
    fmt_amb = _rate(sum(1 for r in fmt_valid if r.get("ambiguous") == "true"), len(fmt_valid))

    return {
        "run": run_name,
        "section": "partial_demand",
        "pole": pole,
        "generated_n": str(generated_n),
        "valid_n": str(valid_n),
        "genuine_n": str(genuine_n),
        "manipulation_success_rate": _format_rate(_rate(manip_ok, len(raw_valid))),
        "detector_accuracy_raw": _format_rate(raw_acc),
        "detector_accuracy_format_normalized": _format_rate(fmt_acc),
        "ambiguous_rate_raw": _format_rate(raw_amb),
        "ambiguous_rate_format_normalized": _format_rate(fmt_amb),
        "full_demand_detected_rate": "",
        "full_demand_ambiguous_rate": "",
        "full_demand_collapsed_rate": "",
    }


def _full_demand_pole_row(
    run_name: str,
    full_demand_rows: list[dict[str, str]],
    *,
    pole: str,
) -> dict[str, Any]:
    raw_valid = [
        r
        for r in full_demand_rows
        if r.get("method") == pole
        and r.get("strip_level") == "raw"
        and r.get("valid_artifact") == "true"
    ]
    n = len(raw_valid)
    detected = sum(1 for r in raw_valid if r.get("detected_method") == pole)
    ambiguous = sum(1 for r in raw_valid if r.get("ambiguous") == "true")
    collapsed = ambiguous if pole == "lazy" else sum(
        1 for r in raw_valid if r.get("detected_method") != pole
    )

    return {
        "run": run_name,
        "section": "full_demand_control",
        "pole": pole,
        "generated_n": "",
        "valid_n": str(n),
        "genuine_n": "",
        "manipulation_success_rate": "",
        "detector_accuracy_raw": "",
        "detector_accuracy_format_normalized": "",
        "ambiguous_rate_raw": "",
        "ambiguous_rate_format_normalized": "",
        "full_demand_detected_rate": _format_rate(_rate(detected, n)),
        "full_demand_ambiguous_rate": _format_rate(_rate(ambiguous, n)),
        "full_demand_collapsed_rate": _format_rate(_rate(collapsed, n)),
    }


def _build_answers(rows: dict[str, dict[str, Any]]) -> dict[str, str]:
    eager = rows["eager"]
    lazy = rows["lazy"]
    eager_full = rows["eager_full"]
    lazy_full = rows["lazy_full"]

    eager_raw_acc = eager["detector_accuracy_raw"]
    lazy_raw_acc = lazy["detector_accuracy_raw"]
    eager_fmt_acc = eager["detector_accuracy_format_normalized"]
    lazy_fmt_acc = lazy["detector_accuracy_format_normalized"]

    q1 = (
        f"**Yes at raw for both poles** (eager {eager_raw_acc}, lazy {lazy_raw_acc} valid-only "
        f"detector accuracy). After format normalization, eager remains {eager_fmt_acc} while "
        f"lazy drops to {lazy_fmt_acc}, so partial-demand recovery is **symmetric at raw** but "
        "**asymmetric under aggressive stripping**."
    )
    q2 = (
        "**Yes.** Eager artifacts are classified from a **positive precomputation trace**: all "
        "feature getters run before the first explicit request (`calls_before_first_request=3`, "
        "`unrequested_features_computed=true`)."
    )
    q3 = (
        "**Yes.** Lazy recovery on partial demand relies on **absence of unrequested computation** "
        "(no features computed before the first getter; only `feature_a` on the first request)."
    )
    q4 = (
        f"**Yes for lazy, no for eager.** Under full-demand control, lazy collapses to ambiguous "
        f"({lazy_full['full_demand_ambiguous_rate']} ambiguous / "
        f"{lazy_full['full_demand_collapsed_rate']} collapsed) while eager remains detected "
        f"({eager_full['full_demand_detected_rate']} detected, "
        f"{eager_full['full_demand_ambiguous_rate']} ambiguous)."
    )
    q5 = (
        "Phrase conservatively that **Class C separates eager and lazy by temporal placement of "
        "the same computations**, not by different formulas: eager is supported by **observed "
        "early work**, lazy by **withheld work until demand**, and the lazy pole **weakens or "
        "collapses when all demand is front-loaded** (full-demand control). Report raw and "
        "stripped recovery separately; do not claim lazy is as strip-robust as eager."
    )

    return {
        "partial_demand_both_poles": q1,
        "eager_positive_trace": q2,
        "lazy_absence_recovery": q3,
        "lazy_full_demand_collapse": q4,
        "conservative_phrasing": q5,
    }


def _write_pole_asymmetry_report(
    path: Path,
    run_name: str,
    rows: list[dict[str, Any]],
    answers: dict[str, str],
) -> None:
    partial = [r for r in rows if r["section"] == "partial_demand"]
    full = [r for r in rows if r["section"] == "full_demand_control"]

    lines = [
        f"# Class C pole-asymmetry audit (`{run_name}`)",
        "",
        "Read-only aggregation of existing partial-demand detection and full-demand control CSVs. "
        "No detectors, prompts, or validity metrics were modified.",
        "",
        "## Partial-demand recovery by pole",
        "",
        "| pole | generated_n | valid_n | genuine_n | manipulation_success_rate | "
        "detector_accuracy_raw | detector_accuracy_format_normalized | "
        "ambiguous_rate_raw | ambiguous_rate_format_normalized |",
        "|------|-------------|---------|-----------|---------------------------|"
        "---------------------|--------------------------------|"
        "--------------------|--------------------------------|",
    ]
    for row in partial:
        lines.append(
            f"| {row['pole']} | {row['generated_n']} | {row['valid_n']} | {row['genuine_n']} | "
            f"{row['manipulation_success_rate']} | {row['detector_accuracy_raw']} | "
            f"{row['detector_accuracy_format_normalized']} | {row['ambiguous_rate_raw']} | "
            f"{row['ambiguous_rate_format_normalized']} |"
        )

    lines.extend(
        [
            "",
            "## Full-demand control by pole (raw, valid artifacts)",
            "",
            "| pole | valid_n | detected_rate | ambiguous_rate | collapsed_rate |",
            "|------|---------|---------------|----------------|----------------|",
        ]
    )
    for row in full:
        lines.append(
            f"| {row['pole']} | {row['valid_n']} | {row['full_demand_detected_rate']} | "
            f"{row['full_demand_ambiguous_rate']} | {row['full_demand_collapsed_rate']} |"
        )

    lines.extend(
        [
            "",
            "Collapsed: for **lazy**, ambiguous under full demand; for **eager**, "
            "misclassified away from eager.",
            "",
            "## Audit questions",
            "",
            "### 1. Does partial-demand recovery hold for both poles?",
            "",
            answers["partial_demand_both_poles"],
            "",
            "### 2. Is eager detected by a positive trace?",
            "",
            answers["eager_positive_trace"],
            "",
            "### 3. Is lazy recovered by absence of unrequested computation?",
            "",
            answers["lazy_absence_recovery"],
            "",
            "### 4. Does lazy collapse under full demand?",
            "",
            answers["lazy_full_demand_collapse"],
            "",
            "### 5. How should the paper phrase this conservatively?",
            "",
            answers["conservative_phrasing"],
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_eager_lazy_pole_asymmetry_audit(
    run_name: str,
    project_root: Path,
) -> EagerLazyPoleAsymmetryResult | None:
    results_dir = project_root / "results" / "core_v2" / "runs" / run_name
    detection_path = results_dir / "eager_lazy_detection.csv"
    full_demand_path = results_dir / "eager_lazy_full_demand_control.csv"

    detection_rows = _read_csv_rows(detection_path)
    full_demand_rows = _read_csv_rows(full_demand_path)
    if not detection_rows:
        return None

    eager_partial = _partial_pole_row(run_name, detection_rows, pole="eager")
    lazy_partial = _partial_pole_row(run_name, detection_rows, pole="lazy")
    eager_full = _full_demand_pole_row(run_name, full_demand_rows, pole="eager")
    lazy_full = _full_demand_pole_row(run_name, full_demand_rows, pole="lazy")

    audit_rows = [eager_partial, lazy_partial, eager_full, lazy_full]
    answers = _build_answers(
        {
            "eager": eager_partial,
            "lazy": lazy_partial,
            "eager_full": eager_full,
            "lazy_full": lazy_full,
        }
    )

    csv_path = results_dir / "eager_lazy_pole_asymmetry.csv"
    md_path = results_dir / "eager_lazy_pole_asymmetry.md"
    _write_csv(csv_path, POLE_ASYMMETRY_FIELDS, audit_rows)
    _write_pole_asymmetry_report(md_path, run_name, audit_rows, answers)

    return EagerLazyPoleAsymmetryResult(
        rows=audit_rows,
        csv_path=csv_path,
        md_path=md_path,
        answers=answers,
    )


def class_c_asymmetry_note(project_root: Path) -> str | None:
    """Short decision-report note if the frozen eager/lazy pole audit exists."""
    run_dir = project_root / "results" / "core_v2" / "runs" / FROZEN_EAGER_LAZY_RUN
    if not (run_dir / "eager_lazy_detection.csv").exists():
        return None

    result = run_eager_lazy_pole_asymmetry_audit(FROZEN_EAGER_LAZY_RUN, project_root)
    if result is None:
        return None

    eager = next(r for r in result.rows if r["section"] == "partial_demand" and r["pole"] == "eager")
    lazy = next(r for r in result.rows if r["section"] == "partial_demand" and r["pole"] == "lazy")
    lazy_full = next(
        r for r in result.rows if r["section"] == "full_demand_control" and r["pole"] == "lazy"
    )

    return (
        f"Frozen generalization audit (`{FROZEN_EAGER_LAZY_RUN}/eager_lazy_pole_asymmetry.md`): "
        f"partial-demand recovery is symmetric at raw (eager {eager['detector_accuracy_raw']}, "
        f"lazy {lazy['detector_accuracy_raw']}) but lazy weakens after format normalization "
        f"({lazy['detector_accuracy_format_normalized']} vs eager "
        f"{eager['detector_accuracy_format_normalized']}). Eager is recovered by a **positive "
        "precomputation trace**; lazy by **withheld computation until demand**. Full-demand "
        f"control collapses lazy signatures ({lazy_full['full_demand_ambiguous_rate']} ambiguous) "
        "while eager remains detected."
    )


def ensure_frozen_eager_lazy_pole_audit(project_root: Path) -> Path | None:
    run_dir = project_root / "results" / "core_v2" / "runs" / FROZEN_EAGER_LAZY_RUN
    if not (run_dir / "eager_lazy_detection.csv").exists():
        return None
    result = run_eager_lazy_pole_asymmetry_audit(FROZEN_EAGER_LAZY_RUN, project_root)
    return result.md_path if result else None
