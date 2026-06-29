from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from invert_core.analyze_run import (
    F11_MAX_AMBIGUOUS,
    F11_MIN_ACCURACY,
    F11_MIN_VALID_N,
    NA,
    _format_rate,
    _model_display_name,
)

DIMENSION_ARTIFACTS: dict[str, dict[str, str]] = {
    "euler_vs_rk4": {
        "valid_only_summary": "integration_valid_only_summary.csv",
        "summary": "integration_summary.csv",
        "report": "integration_report.md",
    },
    "trapezoidal_vs_simpson": {
        "valid_only_summary": "quadrature_valid_only_summary.csv",
        "summary": "quadrature_summary.csv",
        "report": "quadrature_report.md",
    },
}

CLASS_LABELS: dict[str, str] = {
    "euler_vs_rk4": "Class A (derivative-call signatures)",
    "trapezoidal_vs_simpson": "Class B (arithmetic weight signatures)",
}

MODEL_SUMMARY_FIELDS = [
    "run",
    "dimension",
    "model",
    "generated_n",
    "valid_n",
    "valid_artifact_rate",
    "valid_accuracy_raw",
    "valid_accuracy_format_normalized",
    "valid_ambiguous_rate_raw",
    "valid_ambiguous_rate_format_normalized",
    "survives_preregistered_rule",
    "failure_reason",
]

DIMENSION_SUMMARY_FIELDS = [
    "dimension",
    "runs_found",
    "models_evaluated",
    "models_survived",
    "best_model",
    "best_valid_artifact_rate",
    "best_valid_accuracy_format_normalized",
    "status",
]


@dataclass
class SummarizeCoreV2Result:
    model_rows: list[dict[str, Any]] = field(default_factory=list)
    dimension_rows: list[dict[str, Any]] = field(default_factory=list)
    model_summary_path: Path | None = None
    dimension_summary_path: Path | None = None
    decision_report_path: Path | None = None


def _parse_int(value: str) -> int:
    if not value or value == NA:
        return 0
    return int(value)


def _parse_rate(value: str) -> float | None:
    if not value or value == NA:
        return None
    return float(value)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def _weighted_rate(rows: list[dict[str, str]], count_key: str, rate_key: str) -> float | None:
    total = 0
    weighted = 0.0
    for row in rows:
        count = _parse_int(row.get(count_key, "0"))
        rate = _parse_rate(row.get(rate_key, NA))
        if count <= 0 or rate is None:
            continue
        total += count
        weighted += count * rate
    if total == 0:
        return None
    return weighted / total


def _rows_for_model_strip(
    rows: list[dict[str, str]], model: str, strip_level: str
) -> list[dict[str, str]]:
    return [
        r
        for r in rows
        if r.get("model") == model and r.get("strip_level") == strip_level
    ]


def _survives_preregistered_rule(
    valid_n: int,
    raw_acc: float | None,
    fmt_acc: float | None,
    amb_raw: float | None,
    amb_fmt: float | None,
) -> bool:
    return (
        valid_n >= F11_MIN_VALID_N
        and raw_acc is not None
        and raw_acc >= F11_MIN_ACCURACY
        and fmt_acc is not None
        and fmt_acc >= F11_MIN_ACCURACY
        and amb_raw is not None
        and amb_raw <= F11_MAX_AMBIGUOUS
        and amb_fmt is not None
        and amb_fmt <= F11_MAX_AMBIGUOUS
    )


def _failure_reason(
    valid_n: int,
    raw_acc: float | None,
    fmt_acc: float | None,
    amb_raw: float | None,
    amb_fmt: float | None,
    survives: bool,
) -> str:
    if survives:
        return ""
    if valid_n < F11_MIN_VALID_N:
        return "invalid_generation"
    if (
        raw_acc is None
        or raw_acc < F11_MIN_ACCURACY
        or fmt_acc is None
        or fmt_acc < F11_MIN_ACCURACY
        or amb_raw is None
        or amb_raw > F11_MAX_AMBIGUOUS
        or amb_fmt is None
        or amb_fmt > F11_MAX_AMBIGUOUS
    ):
        return "detector_stripping_failure"
    return "other"


def _load_run_dimension(run_dir: Path) -> str | None:
    metadata_path = run_dir / "metadata.json"
    if metadata_path.exists():
        meta = json.loads(metadata_path.read_text(encoding="utf-8"))
        dimension = meta.get("dimension")
        if dimension in DIMENSION_ARTIFACTS:
            return dimension
    for dimension, files in DIMENSION_ARTIFACTS.items():
        if (run_dir / files["valid_only_summary"]).exists() or (
            run_dir / files["summary"]
        ).exists():
            return dimension
    return None


def _run_has_analysis(run_dir: Path, dimension: str) -> bool:
    files = DIMENSION_ARTIFACTS[dimension]
    return (run_dir / files["valid_only_summary"]).exists() or (
        run_dir / files["summary"]
    ).exists()


def _aggregate_model_for_run(
    run_name: str,
    dimension: str,
    model: str,
    summary_rows: list[dict[str, str]],
    valid_only_rows: list[dict[str, str]],
) -> dict[str, Any]:
    raw_summary = _rows_for_model_strip(summary_rows, model, "raw")
    raw_valid = _rows_for_model_strip(valid_only_rows, model, "raw")
    fmt_valid = _rows_for_model_strip(valid_only_rows, model, "format_normalized")

    generated_n = sum(_parse_int(r.get("all_generated_n", "0")) for r in raw_summary)
    valid_n = sum(_parse_int(r.get("valid_n", "0")) for r in raw_valid)
    valid_artifact_rate = valid_n / generated_n if generated_n else None

    raw_acc = _weighted_rate(raw_valid, "valid_n", "valid_detector_accuracy")
    fmt_acc = _weighted_rate(fmt_valid, "valid_n", "valid_detector_accuracy")
    amb_raw = _weighted_rate(raw_valid, "valid_n", "valid_ambiguous_rate")
    amb_fmt = _weighted_rate(fmt_valid, "valid_n", "valid_ambiguous_rate")

    survives = _survives_preregistered_rule(valid_n, raw_acc, fmt_acc, amb_raw, amb_fmt)

    return {
        "run": run_name,
        "dimension": dimension,
        "model": model,
        "generated_n": str(generated_n),
        "valid_n": str(valid_n),
        "valid_artifact_rate": _format_rate(valid_artifact_rate),
        "valid_accuracy_raw": _format_rate(raw_acc),
        "valid_accuracy_format_normalized": _format_rate(fmt_acc),
        "valid_ambiguous_rate_raw": _format_rate(amb_raw),
        "valid_ambiguous_rate_format_normalized": _format_rate(amb_fmt),
        "survives_preregistered_rule": "true" if survives else "false",
        "failure_reason": _failure_reason(
            valid_n, raw_acc, fmt_acc, amb_raw, amb_fmt, survives
        ),
    }


def _dimension_status(models_survived: int, runs_found: int, models_evaluated: int) -> str:
    if runs_found == 0 or models_evaluated == 0:
        return "insufficient_data"
    if models_survived >= 2:
        return "supported_if_2plus_models_survive"
    if models_survived == 1:
        return "promising_if_1_model_survives"
    return "not_supported"


def _best_model_row(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None

    def sort_key(row: dict[str, Any]) -> tuple:
        rate = _parse_rate(str(row.get("valid_artifact_rate", NA)))
        fmt_acc = _parse_rate(str(row.get("valid_accuracy_format_normalized", NA)))
        survives = row.get("survives_preregistered_rule") == "true"
        return (
            0 if survives else 1,
            -(rate if rate is not None else -1.0),
            -(fmt_acc if fmt_acc is not None else -1.0),
        )

    return sorted(rows, key=sort_key)[0]


def _build_dimension_summary(
    dimension: str,
    model_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    dim_rows = [r for r in model_rows if r["dimension"] == dimension]
    runs_found = len({r["run"] for r in dim_rows})
    models_evaluated = len({r["model"] for r in dim_rows if _parse_int(r["generated_n"]) > 0})
    survived_models = {
        r["model"] for r in dim_rows if r["survives_preregistered_rule"] == "true"
    }
    models_survived = len(survived_models)
    best = _best_model_row(dim_rows)
    status = _dimension_status(models_survived, runs_found, models_evaluated)

    return {
        "dimension": dimension,
        "runs_found": str(runs_found),
        "models_evaluated": str(models_evaluated),
        "models_survived": str(models_survived),
        "best_model": best["model"] if best else "",
        "best_valid_artifact_rate": best["valid_artifact_rate"] if best else NA,
        "best_valid_accuracy_format_normalized": (
            best["valid_accuracy_format_normalized"] if best else NA
        ),
        "status": status,
    }


def _class_support_text(status: str, dimension: str, has_data: bool) -> str:
    if not has_data:
        if dimension == "trapezoidal_vs_simpson":
            return "Class B not yet evaluated."
        return "Insufficient completed runs to evaluate."
    if status == "supported_if_2plus_models_survive":
        return (
            f"**Yes (preliminary).** At least two models meet the preregistered valid-only "
            f"survival rule for `{dimension}`."
        )
    if status == "promising_if_1_model_survives":
        return (
            f"**Partially.** One model meets the survival rule for `{dimension}`; a second "
            f"independent survivor is still needed for strong support."
        )
    if status == "not_supported":
        return (
            f"**Not yet.** Completed runs for `{dimension}` do not show any model meeting "
            f"the preregistered survival rule."
        )
    return f"**Insufficient data** for `{dimension}` (no analyzed model outputs found)."


def _next_cheapest_experiment(
    dimension_rows: list[dict[str, Any]],
    model_rows: list[dict[str, Any]],
) -> str:
    by_dim = {r["dimension"]: r for r in dimension_rows}
    euler = by_dim.get("euler_vs_rk4")
    quad = by_dim.get("trapezoidal_vs_simpson")

    if quad and quad["status"] == "insufficient_data":
        return (
            "Run `invert-core analyze-run --run core_v2_quadrature_pilot_local_001` "
            "(or complete quadrature generation first) to evaluate Class B without new API spend."
        )
    if euler and euler["status"] == "promising_if_1_model_survives":
        return (
            "Re-run or expand the local Euler/RK4 pilot with an additional model that already "
            "passed generation validity elsewhere, targeting valid_n >= 12 without paid APIs."
        )
    if (
        euler
        and euler["status"] == "supported_if_2plus_models_survive"
        and quad
        and quad["status"] in ("not_supported", "promising_if_1_model_survives")
    ):
        return (
            "Focus local quadrature generation/analysis on the best-validated model(s) from "
            "Class A before opening any paid API pilots."
        )
    if (
        euler
        and quad
        and euler["status"] == "supported_if_2plus_models_survive"
        and quad["status"] == "supported_if_2plus_models_survive"
    ):
        return (
            "Add the next preregistered Family 1 dimension or a minimal paid-API replication "
            "on the two best local models only."
        )
    invalid_models = [
        r
        for r in model_rows
        if r.get("failure_reason") == "invalid_generation" and _parse_int(r["generated_n"]) > 0
    ]
    if invalid_models:
        return (
            "Improve generation validity first (local_stub or best local model), then re-analyze "
            "existing runs before adding models or dimensions."
        )
    return (
        "Complete analyze-run for any generated but unanalyzed Core v2 runs, then re-run "
        "`invert-core summarize-core-v2`."
    )


def _write_decision_report(
    path: Path,
    model_rows: list[dict[str, Any]],
    dimension_rows: list[dict[str, Any]],
) -> None:
    by_dim = {r["dimension"]: r for r in dimension_rows}
    euler = by_dim.get("euler_vs_rk4")
    quad = by_dim.get("trapezoidal_vs_simpson")

    enough_evidence = [
        CLASS_LABELS[d]
        for d, row in by_dim.items()
        if row["status"] in ("supported_if_2plus_models_survive", "promising_if_1_model_survives")
        and _parse_int(row["runs_found"]) > 0
    ]

    reliable_models = sorted(
        {
            _model_display_name(r["model"])
            for r in model_rows
            if r["survives_preregistered_rule"] == "true"
        }
    )

    invalid_failures = sorted(
        {
            f"{r['run']} / {_model_display_name(r['model'])} ({r['dimension']})"
            for r in model_rows
            if r.get("failure_reason") == "invalid_generation"
        }
    )

    detector_failures = sorted(
        {
            f"{r['run']} / {_model_display_name(r['model'])} ({r['dimension']})"
            for r in model_rows
            if r.get("failure_reason") == "detector_stripping_failure"
        }
    )

    class_a = _class_support_text(
        euler["status"] if euler else "insufficient_data",
        "euler_vs_rk4",
        bool(euler and _parse_int(euler["runs_found"]) > 0),
    )
    class_b = _class_support_text(
        quad["status"] if quad else "insufficient_data",
        "trapezoidal_vs_simpson",
        bool(quad and _parse_int(quad["runs_found"]) > 0),
    )

    classes_with_strong = sum(
        1
        for row in dimension_rows
        if row["status"] == "supported_if_2plus_models_survive"
    )
    classes_with_promising = sum(
        1
        for row in dimension_rows
        if row["status"] == "promising_if_1_model_survives"
    )

    if classes_with_strong >= 2:
        two_class_text = (
            "**Close.** Two mechanistically distinct classes each have >=2 surviving models "
            "under the preregistered valid-only rule; confirm with independent replication "
            "before strong claims."
        )
    elif classes_with_strong == 1 and classes_with_promising >= 1:
        two_class_text = (
            "**Partially close.** One class meets the 2-model threshold and another is "
            "promising (1 survivor); the two-class criterion is not yet met."
        )
    elif classes_with_promising >= 1 or classes_with_strong == 1:
        two_class_text = (
            "**Not yet close.** Evidence exists for at least one class, but two independent "
            "classes with >=2 surviving models have not been demonstrated."
        )
    else:
        two_class_text = (
            "**Not close.** Insufficient cross-run evidence to support two mechanistically "
            "distinct classes under the preregistered criterion."
        )

    lines = [
        "# INVERT Core v2 — Cross-Run Decision Report",
        "",
        "Aggregated from completed runs under `results/core_v2/runs/`. "
        "Missing per-run files are skipped gracefully.",
        "",
        "## 1. Which dimensions have enough evidence?",
        "",
    ]
    if enough_evidence:
        for item in enough_evidence:
            lines.append(f"- {item}")
    else:
        lines.append("- None with strong cross-run support yet.")

    lines.extend(["", "## 2. Which models are reliable generators?", ""])
    if reliable_models:
        for name in reliable_models:
            lines.append(f"- {name}")
    else:
        lines.append("- None meet the preregistered survival rule in completed runs.")

    lines.extend(["", "## 3. Generation validity failures", ""])
    if invalid_failures:
        for item in invalid_failures:
            lines.append(f"- {item}")
    else:
        lines.append("- None identified (valid_n >= 12 or other failure modes).")

    lines.extend(["", "## 4. Detector / stripping failures", ""])
    if detector_failures:
        for item in detector_failures:
            lines.append(f"- {item}")
    else:
        lines.append("- None identified at the model-run aggregate level.")

    lines.extend(
        [
            "",
            "## 5. Is Class A supported?",
            "",
            class_a,
            "",
            "## 6. Is Class B supported?",
            "",
            class_b if quad and _parse_int(quad["runs_found"]) > 0 else "Class B not yet evaluated.",
            "",
            "## 7. Two mechanistically distinct classes (preregistered criterion)",
            "",
            two_class_text,
            "",
            "## 8. Next cheapest experiment",
            "",
            _next_cheapest_experiment(dimension_rows, model_rows),
            "",
            "## Dimension status snapshot",
            "",
            "| dimension | runs_found | models_evaluated | models_survived | status |",
            "|-----------|------------|------------------|-----------------|--------|",
        ]
    )
    for row in dimension_rows:
        lines.append(
            f"| {row['dimension']} | {row['runs_found']} | {row['models_evaluated']} | "
            f"{row['models_survived']} | {row['status']} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_summarize_core_v2(project_root: Path) -> SummarizeCoreV2Result:
    runs_root = project_root / "results" / "core_v2" / "runs"
    output_root = project_root / "results" / "core_v2"

    model_rows: list[dict[str, Any]] = []

    if runs_root.exists():
        for run_dir in sorted(runs_root.iterdir()):
            if not run_dir.is_dir():
                continue
            dimension = _load_run_dimension(run_dir)
            if dimension is None or not _run_has_analysis(run_dir, dimension):
                continue

            files = DIMENSION_ARTIFACTS[dimension]
            summary_rows = _read_csv(run_dir / files["summary"])
            valid_only_rows = _read_csv(run_dir / files["valid_only_summary"])
            if not summary_rows and not valid_only_rows:
                continue

            models = sorted(
                {r.get("model", "") for r in summary_rows + valid_only_rows if r.get("model")}
            )
            for model in models:
                model_rows.append(
                    _aggregate_model_for_run(
                        run_dir.name,
                        dimension,
                        model,
                        summary_rows,
                        valid_only_rows,
                    )
                )

    dimension_rows = [
        _build_dimension_summary(dimension, model_rows)
        for dimension in DIMENSION_ARTIFACTS
    ]

    model_summary_path = output_root / "core_v2_model_dimension_summary.csv"
    dimension_summary_path = output_root / "core_v2_dimension_summary.csv"
    decision_report_path = output_root / "core_v2_decision_report.md"

    _write_csv(model_summary_path, MODEL_SUMMARY_FIELDS, model_rows)
    _write_csv(dimension_summary_path, DIMENSION_SUMMARY_FIELDS, dimension_rows)
    _write_decision_report(decision_report_path, model_rows, dimension_rows)

    return SummarizeCoreV2Result(
        model_rows=model_rows,
        dimension_rows=dimension_rows,
        model_summary_path=model_summary_path,
        dimension_summary_path=dimension_summary_path,
        decision_report_path=decision_report_path,
    )
