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
    F13_MIN_VALID_N,
    NA,
    _format_rate,
    _model_display_name,
)
from invert_core.frozen_detector import is_frozen_generalization_run

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
    "eager_vs_lazy": {
        "valid_only_summary": "eager_lazy_valid_only_summary.csv",
        "summary": "eager_lazy_summary.csv",
        "report": "eager_lazy_report.md",
    },
    "bfs_vs_dfs": {
        "valid_only_summary": "bfs_dfs_valid_only_summary.csv",
        "summary": "bfs_dfs_summary.csv",
        "report": "bfs_dfs_report.md",
    },
    "deterministic_vs_randomized": {
        "valid_only_summary": "deterministic_randomized_valid_only_summary.csv",
        "summary": "deterministic_randomized_summary.csv",
        "report": "deterministic_randomized_report.md",
    },
}

CLASS_LABELS: dict[str, str] = {
    "euler_vs_rk4": "Class A (derivative-call signatures)",
    "trapezoidal_vs_simpson": "Class B (arithmetic weight signatures)",
    "eager_vs_lazy": "Class C (dynamic temporal / avoidable-computation signatures)",
    "bfs_vs_dfs": "Class D (dynamic order process signatures)",
    "deterministic_vs_randomized": (
        "Class E (dynamic inter-execution variability signatures)"
    ),
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


def _min_valid_n_for_dimension(dimension: str) -> int:
    if dimension in ("eager_vs_lazy", "bfs_vs_dfs", "deterministic_vs_randomized"):
        return F13_MIN_VALID_N
    return F11_MIN_VALID_N


def _survives_preregistered_rule(
    valid_n: int,
    raw_acc: float | None,
    fmt_acc: float | None,
    amb_raw: float | None,
    amb_fmt: float | None,
    *,
    min_valid_n: int = F11_MIN_VALID_N,
) -> bool:
    return (
        valid_n >= min_valid_n
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
    *,
    min_valid_n: int = F11_MIN_VALID_N,
) -> str:
    if survives:
        return ""
    if valid_n < min_valid_n:
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


def _run_kind(run_dir: Path) -> str:
    if is_frozen_generalization_run(run_dir):
        return "frozen_generalization"
    return "development"


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
    *,
    run_kind: str,
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

    min_valid_n = _min_valid_n_for_dimension(dimension)
    survives = _survives_preregistered_rule(
        valid_n, raw_acc, fmt_acc, amb_raw, amb_fmt, min_valid_n=min_valid_n
    )

    return {
        "run": run_name,
        "run_kind": run_kind,
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
            valid_n, raw_acc, fmt_acc, amb_raw, amb_fmt, survives, min_valid_n=min_valid_n
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
        if dimension == "eager_vs_lazy":
            return "Class C not yet evaluated."
        if dimension == "bfs_vs_dfs":
            return "Class D not yet evaluated."
        if dimension == "deterministic_vs_randomized":
            return "Class E not yet evaluated."
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
    eager_lazy = by_dim.get("eager_vs_lazy")
    bfs_dfs = by_dim.get("bfs_vs_dfs")
    det_rand = by_dim.get("deterministic_vs_randomized")

    if det_rand and det_rand["status"] == "insufficient_data":
        return (
            "Run `./scripts/run_core_v2_generalization_local_deterministic_randomized_001.sh` "
            "(or analyze an existing Class E pilot) to evaluate deterministic/randomized "
            "without paid APIs."
        )
    if bfs_dfs and bfs_dfs["status"] == "insufficient_data":
        return (
            "Run `invert-core analyze-run --run core_v2_bfs_dfs_pilot_local_001` "
            "(or complete bfs/dfs generation first) to evaluate Class D without new API spend."
        )
    if eager_lazy and eager_lazy["status"] == "insufficient_data":
        return (
            "Run `invert-core analyze-run --run core_v2_eager_lazy_pilot_local_001` "
            "(or complete eager/lazy generation first) to evaluate Class C without new API spend."
        )
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


def _aggregate_frozen_dimension_evidence(
    dimension: str,
    model_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [
        r
        for r in model_rows
        if r["dimension"] == dimension and r.get("run_kind") == "frozen_generalization"
    ]
    if not rows:
        return {
            "has_data": False,
            "models_evaluated": [],
            "models_survived": [],
            "valid_artifact_rate": None,
            "valid_accuracy_raw": None,
            "valid_accuracy_format_normalized": None,
            "valid_ambiguous_rate_raw": None,
        }

    models_evaluated = sorted({_model_display_name(r["model"]) for r in rows})
    models_survived = sorted(
        {
            _model_display_name(r["model"])
            for r in rows
            if r.get("survives_preregistered_rule") == "true"
        }
    )

    generated_total = sum(_parse_int(r["generated_n"]) for r in rows)
    valid_total = sum(_parse_int(r["valid_n"]) for r in rows)
    valid_rate = valid_total / generated_total if generated_total else None

    raw_acc = _weighted_rate_from_model_rows(rows, "valid_accuracy_raw", "valid_n")
    fmt_acc = _weighted_rate_from_model_rows(rows, "valid_accuracy_format_normalized", "valid_n")
    amb_raw = _weighted_rate_from_model_rows(rows, "valid_ambiguous_rate_raw", "valid_n")

    return {
        "has_data": True,
        "models_evaluated": models_evaluated,
        "models_survived": models_survived,
        "valid_artifact_rate": valid_rate,
        "valid_accuracy_raw": raw_acc,
        "valid_accuracy_format_normalized": fmt_acc,
        "valid_ambiguous_rate_raw": amb_raw,
    }


def _weighted_rate_from_model_rows(
    rows: list[dict[str, Any]],
    rate_key: str,
    weight_key: str,
) -> float | None:
    total = 0
    weighted = 0.0
    for row in rows:
        weight = _parse_int(str(row.get(weight_key, "0")))
        rate = _parse_rate(str(row.get(rate_key, NA)))
        if weight <= 0 or rate is None:
            continue
        total += weight
        weighted += weight * rate
    if total == 0:
        return None
    return weighted / total


def _write_decision_report(
    path: Path,
    model_rows: list[dict[str, Any]],
    dimension_rows: list[dict[str, Any]],
    *,
    development_runs: list[str],
    frozen_runs: list[str],
    project_root: Path,
) -> None:
    by_dim = {r["dimension"]: r for r in dimension_rows}
    euler = by_dim.get("euler_vs_rk4")
    quad = by_dim.get("trapezoidal_vs_simpson")
    eager_lazy = by_dim.get("eager_vs_lazy")
    bfs_dfs = by_dim.get("bfs_vs_dfs")
    det_rand = by_dim.get("deterministic_vs_randomized")

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
    class_c = _class_support_text(
        eager_lazy["status"] if eager_lazy else "insufficient_data",
        "eager_vs_lazy",
        bool(eager_lazy and _parse_int(eager_lazy["runs_found"]) > 0),
    )
    class_d = _class_support_text(
        bfs_dfs["status"] if bfs_dfs else "insufficient_data",
        "bfs_vs_dfs",
        bool(bfs_dfs and _parse_int(bfs_dfs["runs_found"]) > 0),
    )
    class_e = _class_support_text(
        det_rand["status"] if det_rand else "insufficient_data",
        "deterministic_vs_randomized",
        bool(det_rand and _parse_int(det_rand["runs_found"]) > 0),
    )

    class_c_passes = (
        eager_lazy is not None
        and eager_lazy["status"] in ("supported_if_2plus_models_survive", "promising_if_1_model_survives")
        and _parse_int(eager_lazy["runs_found"]) > 0
    )
    frozen_c = _aggregate_frozen_dimension_evidence("eager_vs_lazy", model_rows)
    if frozen_c["has_data"]:
        process_signature_text = (
            "Frozen generalization evidence for Class C is available "
            f"(models evaluated: {', '.join(frozen_c['models_evaluated']) or 'none'}; "
            f"models survived: {', '.join(frozen_c['models_survived']) or 'none'}). "
            "This result is not reducible to mathematical-coefficient identity because "
            "eager and lazy compute the same feature formulas; only timing of computation differs."
        )
    elif class_c_passes:
        process_signature_text = (
            "This result is not reducible to mathematical-coefficient identity because "
            "eager and lazy compute the same feature formulas; only timing of computation differs."
        )
    else:
        process_signature_text = (
            "Current evidence remains limited to arithmetic/static signatures."
        )

    from invert_core.audit_eager_lazy_pole_asymmetry import class_c_asymmetry_note

    class_c_asymmetry = class_c_asymmetry_note(project_root)

    class_d_passes = (
        bfs_dfs is not None
        and bfs_dfs["status"] in ("supported_if_2plus_models_survive", "promising_if_1_model_survives")
        and _parse_int(bfs_dfs["runs_found"]) > 0
    )
    frozen_d = _aggregate_frozen_dimension_evidence("bfs_vs_dfs", model_rows)
    if frozen_d["has_data"]:
        order_signature_text = (
            "Frozen generalization evidence for Class D is available "
            f"(models evaluated: {', '.join(frozen_d['models_evaluated']) or 'none'}; "
            f"models survived: {', '.join(frozen_d['models_survived']) or 'none'}). "
            "This result is not reducible to mathematical identity or avoidable-computation "
            "detection because BFS and DFS visit the same reachable set and perform the same "
            "amount of node visitation; only traversal order differs."
        )
    elif class_d_passes:
        order_signature_text = (
            "This result is not reducible to mathematical identity or avoidable-computation "
            "detection because BFS and DFS visit the same reachable set and perform the same "
            "amount of node visitation; only traversal order differs."
        )
    else:
        order_signature_text = (
            "Class D (dynamic order signatures) not yet supported by completed runs."
        )

    class_e_passes = (
        det_rand is not None
        and det_rand["status"]
        in ("supported_if_2plus_models_survive", "promising_if_1_model_survives")
        and _parse_int(det_rand["runs_found"]) > 0
    )
    frozen_e = _aggregate_frozen_dimension_evidence("deterministic_vs_randomized", model_rows)
    variability_signature_text = (
        "This result is not reducible to mathematical identity, avoidable computation, "
        "or traversal order because the same input and same behavioral output produce "
        "stable versus variable traces across repeated executions."
    )
    if frozen_e["has_data"]:
        variability_signature_text = (
            "Frozen generalization evidence for Class E is available "
            f"(models evaluated: {', '.join(frozen_e['models_evaluated']) or 'none'}; "
            f"models survived: {', '.join(frozen_e['models_survived']) or 'none'}). "
            + variability_signature_text
        )
    elif not class_e_passes:
        variability_signature_text = (
            "Class E (dynamic inter-execution variability signatures) not yet supported "
            "by completed runs."
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
        "Signature classes under evaluation:",
        "- Class A: arithmetic count signatures (`euler_vs_rk4`)",
        "- Class B: arithmetic weight signatures (`trapezoidal_vs_simpson`)",
        "- Class C: dynamic temporal / avoidable-computation signatures (`eager_vs_lazy`)",
        "- Class D: dynamic order process signatures (`bfs_vs_dfs`)",
        "- Class E: dynamic inter-execution variability signatures (`deterministic_vs_randomized`)",
        "",
        "## Run inventory",
        "",
        "### Development runs",
        "",
    ]
    if development_runs:
        for run in development_runs:
            lines.append(f"- `{run}`")
    else:
        lines.append("- None with analyzed outputs.")

    lines.extend(["", "### Frozen generalization runs", ""])
    if frozen_runs:
        for run in frozen_runs:
            lines.append(f"- `{run}` (has `frozen_detector_metadata.json`)")
    else:
        lines.append("- None yet.")

    lines.extend(["", "## 1. Which dimensions have enough evidence?", ""])
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
            "## 7. Is Class C supported?",
            "",
            class_c if eager_lazy and _parse_int(eager_lazy["runs_found"]) > 0 else "Class C not yet evaluated.",
            "",
            "## 8. Process signature vs mathematical identity (F1.3 / Class C)",
            "",
            process_signature_text,
            "",
            "## 8.1 Class C pole asymmetry (frozen generalization audit)",
            "",
            class_c_asymmetry
            if class_c_asymmetry
            else "No pole-asymmetry audit found for frozen eager/lazy generalization.",
            "",
            "## 9. Is Class D supported?",
            "",
            class_d if bfs_dfs and _parse_int(bfs_dfs["runs_found"]) > 0 else "Class D not yet evaluated.",
            "",
            "## 10. Order signature vs mathematical identity (F1.4 / Class D)",
            "",
            order_signature_text,
            "",
            "## 11. Is Class E supported?",
            "",
            class_e if det_rand and _parse_int(det_rand["runs_found"]) > 0 else "Class E not yet evaluated.",
            "",
            "## 12. Inter-execution variability vs other signature classes (F1.5 / Class E)",
            "",
            variability_signature_text,
            "",
            "## 13. Two mechanistically distinct classes (preregistered criterion)",
            "",
            two_class_text,
            "",
            "## 14. Next cheapest experiment",
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

    lines.extend(["", "## Frozen generalization evidence", ""])
    for dimension in DIMENSION_ARTIFACTS:
        evidence = _aggregate_frozen_dimension_evidence(dimension, model_rows)
        label = CLASS_LABELS[dimension]
        lines.extend([f"### {label} (`{dimension}`)", ""])
        if not evidence["has_data"]:
            lines.append("- No frozen generalization runs analyzed for this dimension yet.")
            lines.append("")
            continue
        if dimension == "eager_vs_lazy":
            lines.append(
                "- Frozen detector metadata includes SHA256 of `eager_lazy.py` and `stripping.py` "
                "when analyzed via `core_v2_generalization_local_eager_lazy_001`."
            )
        if dimension == "bfs_vs_dfs":
            lines.append(
                "- Frozen detector metadata includes SHA256 of `bfs_dfs.py` and `stripping.py` "
                "when analyzed via `core_v2_generalization_local_bfs_dfs_001`."
            )
        if dimension == "deterministic_vs_randomized":
            lines.append(
                "- Frozen detector metadata includes SHA256 of `deterministic_randomized.py` "
                "and `stripping.py` when analyzed via "
                "`core_v2_generalization_local_deterministic_randomized_001`."
            )
        lines.append(
            f"- Models evaluated: {', '.join(evidence['models_evaluated']) or 'none'}"
        )
        lines.append(
            f"- Models survived: {', '.join(evidence['models_survived']) or 'none'}"
        )
        lines.append(
            f"- Valid artifact rate: {_format_rate(evidence['valid_artifact_rate'])}"
        )
        lines.append(
            f"- Detector accuracy (raw): {_format_rate(evidence['valid_accuracy_raw'])}"
        )
        lines.append(
            "- Detector accuracy (format_normalized): "
            f"{_format_rate(evidence['valid_accuracy_format_normalized'])}"
        )
        lines.append(
            f"- Ambiguous rate (raw): {_format_rate(evidence['valid_ambiguous_rate_raw'])}"
        )
        lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_summarize_core_v2(project_root: Path) -> SummarizeCoreV2Result:
    runs_root = project_root / "results" / "core_v2" / "runs"
    output_root = project_root / "results" / "core_v2"

    model_rows: list[dict[str, Any]] = []
    development_runs: list[str] = []
    frozen_runs: list[str] = []

    if runs_root.exists():
        for run_dir in sorted(runs_root.iterdir()):
            if not run_dir.is_dir():
                continue
            dimension = _load_run_dimension(run_dir)
            if dimension is None or not _run_has_analysis(run_dir, dimension):
                continue

            kind = _run_kind(run_dir)
            if kind == "frozen_generalization":
                frozen_runs.append(run_dir.name)
            else:
                development_runs.append(run_dir.name)

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
                        run_kind=kind,
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
    _write_decision_report(
        decision_report_path,
        model_rows,
        dimension_rows,
        development_runs=sorted(development_runs),
        frozen_runs=sorted(frozen_runs),
        project_root=project_root,
    )

    return SummarizeCoreV2Result(
        model_rows=model_rows,
        dimension_rows=dimension_rows,
        model_summary_path=model_summary_path,
        dimension_summary_path=dimension_summary_path,
        decision_report_path=decision_report_path,
    )
