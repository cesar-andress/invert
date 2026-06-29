from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from invert_core.analyze_run import (
    F11_MAX_AMBIGUOUS,
    F11_MIN_ACCURACY,
    F11_MIN_VALID_N,
    RunAnalysisResult,
    _aggregate_model_strip_valid,
    _bool_str,
    _build_all_generated_summary,
    _build_model_rankings,
    _build_valid_only_summary,
    _compute_stats,
    _format_rate,
    _iter_code_artifacts,
    _model_display_name,
    _read_code,
    _sweep_conclusions,
    _write_csv,
)
from invert_core.detectors.quadrature import detect_quadrature
from invert_core.pilot_config import CoreV2PilotConfig
from invert_core.quadrature_behavioral import run_quadrature_behavioral_oracle
from invert_core.quadrature_tasks import QuadratureTask, load_quadrature_tasks


def _quadrature_entry(strip_level: str) -> str | None:
    if strip_level in ("raw", "no_comments"):
        return "integrate"
    return None


def _load_tasks_by_id(tasks_file: Path) -> dict[str, QuadratureTask]:
    return {t.task_id: t for t in load_quadrature_tasks(tasks_file)}


def _coeffs_csv(coeffs: list[float]) -> str:
    return ";".join(str(c) for c in coeffs)


def _detection_fields() -> list[str]:
    return [
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


def run_quadrature_analyze_run(
    run_name: str,
    project_root: Path,
    *,
    config_path: Path | None = None,
) -> RunAnalysisResult:
    data_root = project_root / "data" / "core_v2"
    results_dir = project_root / "results" / "core_v2" / "runs" / run_name
    results_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = results_dir / "metadata.json"
    if config_path is None and metadata_path.exists():
        meta = json.loads(metadata_path.read_text(encoding="utf-8"))
        tasks_file = project_root / "data" / "core_v2" / "tasks" / "quadrature_tasks.json"
        strip_levels = meta.get(
            "strip_levels",
            ["raw", "no_comments", "renamed", "no_imports", "format_normalized"],
        )
    elif config_path is not None:
        pilot = CoreV2PilotConfig.from_yaml(config_path, project_root)
        tasks_file = pilot.tasks_file
        strip_levels = pilot.strip_levels
    else:
        tasks_file = project_root / "data" / "core_v2" / "tasks" / "quadrature_tasks.json"
        strip_levels = ["raw", "no_comments", "renamed", "no_imports", "format_normalized"]

    tasks_by_id = _load_tasks_by_id(tasks_file)
    artifacts = _iter_code_artifacts(run_name, data_root)

    detection_rows: list[dict[str, Any]] = []
    behavioral_cache: dict[str, Any] = {}

    for art in artifacts:
        code_path: Path = art["code_path"]
        task = tasks_by_id.get(art["task_id"])
        cache_key = str(code_path)
        if cache_key not in behavioral_cache:
            if task and code_path.exists():
                behavioral_cache[cache_key] = run_quadrature_behavioral_oracle(
                    code_path.read_text(encoding="utf-8"), task
                )
            else:
                behavioral_cache[cache_key] = None
        behavioral = behavioral_cache[cache_key]

        parsed = behavioral.parsed if behavioral else False
        behavioral_pass = behavioral.behavioral_pass if behavioral else False
        valid_artifact = parsed and behavioral_pass

        for strip_level in strip_levels:
            stripped_path = (
                data_root
                / "stripped"
                / run_name
                / strip_level
                / art["model"]
                / art["task_id"]
                / art["method"]
                / f"rep_{art['rep']}.py"
            )
            code = _read_code(code_path, stripped_path, strip_level)
            if not code.strip():
                continue

            result = detect_quadrature(code, entry_function=_quadrature_entry(strip_level))
            predicted = result.method
            true_method = art["method"]
            detector_correct = predicted == true_method
            ev = result.evidence

            detection_rows.append(
                {
                    "run": run_name,
                    "model": art["model"],
                    "task_id": art["task_id"],
                    "method": true_method,
                    "rep": art["rep"],
                    "strip_level": strip_level,
                    "parsed": _bool_str(parsed),
                    "behavioral_pass": _bool_str(behavioral_pass),
                    "valid_artifact": _bool_str(valid_artifact),
                    "detected_method": predicted,
                    "detector_correct": _bool_str(detector_correct),
                    "ambiguous": _bool_str(predicted == "ambiguous"),
                    "has_endpoint_half_weights": _bool_str(
                        bool(ev.get("has_endpoint_half_weights"))
                    ),
                    "has_simpson_4_2_pattern": _bool_str(
                        bool(ev.get("has_simpson_4_2_pattern"))
                    ),
                    "coefficient_literals": _coeffs_csv(ev.get("coefficient_literals", [])),
                    "function_eval_pattern": ev.get("function_eval_pattern", ""),
                }
            )

    summary_rows = _build_all_generated_summary(detection_rows)
    valid_summary_rows = _build_valid_only_summary(detection_rows)
    stats = _compute_stats(detection_rows, artifacts)

    detection_path = results_dir / "quadrature_detection.csv"
    summary_path = results_dir / "quadrature_summary.csv"
    valid_summary_path = results_dir / "quadrature_valid_only_summary.csv"
    report_path = results_dir / "quadrature_report.md"

    _write_csv(detection_path, _detection_fields(), detection_rows)
    _write_csv(summary_path, _all_generated_summary_fields(), summary_rows)
    _write_csv(valid_summary_path, _valid_only_summary_fields(), valid_summary_rows)
    _write_quadrature_report(
        report_path,
        run_name,
        stats,
        summary_rows,
        valid_summary_rows,
        detection_rows,
    )

    return RunAnalysisResult(
        detection_rows=detection_rows,
        summary_rows=summary_rows,
        valid_summary_rows=valid_summary_rows,
        report_path=report_path,
        detection_path=detection_path,
        summary_path=summary_path,
        valid_summary_path=valid_summary_path,
        stats=stats,
    )


def _all_generated_summary_fields() -> list[str]:
    return [
        "model",
        "task_id",
        "method",
        "strip_level",
        "all_generated_n",
        "all_generated_detector_accuracy",
        "all_generated_behavioral_pass_rate",
        "all_generated_ambiguous_rate",
    ]


def _valid_only_summary_fields() -> list[str]:
    return [
        "model",
        "task_id",
        "method",
        "strip_level",
        "valid_n",
        "valid_detector_accuracy",
        "valid_ambiguous_rate",
    ]


def _f12_survival_for_model(detection_rows: list[dict[str, Any]], model: str) -> dict[str, Any]:
    raw = _aggregate_model_strip_valid(detection_rows, model, "raw")
    fmt = _aggregate_model_strip_valid(detection_rows, model, "format_normalized")
    valid_n = raw["valid_n"]
    survives = (
        valid_n >= F11_MIN_VALID_N
        and raw["valid_detector_accuracy"] is not None
        and raw["valid_detector_accuracy"] >= F11_MIN_ACCURACY
        and fmt["valid_detector_accuracy"] is not None
        and fmt["valid_detector_accuracy"] >= F11_MIN_ACCURACY
        and raw["valid_ambiguous_rate"] is not None
        and raw["valid_ambiguous_rate"] <= F11_MAX_AMBIGUOUS
    )
    return {
        "valid_n_raw": valid_n,
        "raw_accuracy": raw["valid_detector_accuracy"],
        "format_normalized_accuracy": fmt["valid_detector_accuracy"],
        "raw_ambiguous_rate": raw["valid_ambiguous_rate"],
        "format_normalized_ambiguous_rate": fmt["valid_ambiguous_rate"],
        "survives": survives,
    }


def _write_quadrature_report(
    path: Path,
    run_name: str,
    stats: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    valid_summary_rows: list[dict[str, Any]],
    detection_rows: list[dict[str, Any]],
) -> None:
    models = sorted({r["model"] for r in detection_rows})
    model_f12 = {model: _f12_survival_for_model(detection_rows, model) for model in models}
    stats = {**stats, "model_f11": model_f12}

    raw_valid_by_model = {
        model: _aggregate_model_strip_valid(detection_rows, model, "raw") for model in models
    }
    fmt_valid_by_model = {
        model: _aggregate_model_strip_valid(detection_rows, model, "format_normalized")
        for model in models
    }

    model_rankings = _build_model_rankings(detection_rows, model_f12)
    for row in model_rankings:
        row["f1_1_survives"] = row.pop("f1_1_survives", False)
        row["f1_2_survives"] = model_f12.get(row["model"], {}).get("survives", False)

    conclusions = _sweep_conclusions(
        [{**r, "f1_1_survives": r.get("f1_2_survives", False)} for r in model_rankings]
    )

    def _f12_answer(model_key: str, f12: dict[str, Any]) -> str:
        if model_key not in models:
            return f"**No data** for {_model_display_name(model_key)} in this run."
        if f12.get("survives"):
            return (
                f"**Yes.** {_model_display_name(model_key)} meets preregistered F1.2 thresholds "
                f"on valid artifacts (valid_n={f12.get('valid_n_raw')}, "
                f"raw accuracy={_format_rate(f12.get('raw_accuracy'))}, "
                f"format_normalized accuracy={_format_rate(f12.get('format_normalized_accuracy'))}, "
                f"ambiguous rate={_format_rate(f12.get('raw_ambiguous_rate'))})."
            )
        return (
            f"**No / not yet.** {_model_display_name(model_key)} does not meet all F1.2 thresholds "
            f"(valid_n={f12.get('valid_n_raw', 0)}, "
            f"raw accuracy={_format_rate(f12.get('raw_accuracy'))}, "
            f"format_normalized accuracy={_format_rate(f12.get('format_normalized_accuracy'))}, "
            f"ambiguous rate={_format_rate(f12.get('raw_ambiguous_rate'))})."
        )

    lines = [
        f"# INVERT Core v2 — F1.2 Quadrature Report (`{run_name}`)",
        "",
        "## 1. Generation validity",
        "",
        f"- Generated artifacts: **{stats['n_artifacts']}**",
        f"- Parsed at raw level: **{stats['n_parsed']}**",
        f"- Valid behavioral artifacts: **{stats['n_valid']}**",
        f"- Invalid artifacts (manipulation/validity failures): **{stats['n_invalid']}**",
        "",
        "Invalid artifacts by model/task/method (raw level):",
        "",
    ]
    if stats["invalid_by_group"]:
        for key, count in stats["invalid_by_group"].items():
            lines.append(f"- `{key}`: {count}")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "Invalid artifacts are **not** recovery failures; they failed the behavioral oracle "
            "and are excluded from valid-only recovery metrics.",
            "",
            "## 2. Model ranking (valid-only recovery)",
            "",
            "| rank | model | generated_n | valid_n | valid_artifact_rate | "
            "valid_accuracy_raw | valid_accuracy_format_normalized | "
            "valid_ambiguous_rate_raw | f1_2_survives |",
            "|------|-------|-------------|---------|---------------------|"
            "---------------------|--------------------------------|"
            "--------------------------|---------------|",
        ]
    )
    for row in model_rankings:
        lines.append(
            f"| {row['rank']} | {row['display_name']} | {row['generated_n']} | {row['valid_n']} | "
            f"{_format_rate(row['valid_artifact_rate'])} | "
            f"{_format_rate(row['valid_accuracy_raw'])} | "
            f"{_format_rate(row['valid_accuracy_format_normalized'])} | "
            f"{_format_rate(row['valid_ambiguous_rate_raw'])} | "
            f"{'pass' if row.get('f1_2_survives') else 'fail'} |"
        )

    lines.extend(
        [
            "",
            "## 3. Local model conclusions",
            "",
            "### Models supporting F1.2",
            "",
        ]
    )
    if conclusions["f1_1_support"]:
        lines.append("- " + ", ".join(conclusions["f1_1_support"]))
    else:
        lines.append("- None in this run.")

    lines.extend(
        [
            "",
            "## 4. Recovery on valid artifacts only",
            "",
            "| model | strip_level | valid_n | valid_detector_accuracy | valid_ambiguous_rate |",
            "|-------|-------------|---------|-------------------------|----------------------|",
        ]
    )
    for row in valid_summary_rows:
        if row["valid_n"] == "0":
            continue
        if row["strip_level"] not in ("raw", "format_normalized"):
            continue
        lines.append(
            f"| {row['model']} | {row['strip_level']} | {row['valid_n']} | "
            f"{row['valid_detector_accuracy']} | {row['valid_ambiguous_rate']} |"
        )

    lines.extend(
        [
            "",
            "## 5. F1.2 decision (per model)",
            "",
            f"Preregistered rule: valid_n >= {F11_MIN_VALID_N}, valid_detector_accuracy >= "
            f"{F11_MIN_ACCURACY} at raw and format_normalized, valid_ambiguous_rate <= "
            f"{F11_MAX_AMBIGUOUS}.",
            "",
        ]
    )
    for row in model_rankings:
        f12 = model_f12.get(row["model"], {})
        lines.extend(
            [
                f"### {_model_display_name(row['model'])}",
                "",
                _f12_answer(row["model"], f12),
                "",
            ]
        )

    lines.extend(
        [
            "### Should invalid artifacts be interpreted as recovery failure?",
            "",
            "**No.** Invalid artifacts failed behavioral validation (parse/runtime/tolerance). "
            "They are manipulation/validity failures and must not enter valid-only recovery metrics.",
            "",
            "## 6. All-generated summary (includes invalid artifacts)",
            "",
            "| model | task | method | strip_level | all_generated_n | accuracy | behavioral_pass | ambiguous |",
            "|-------|------|--------|-------------|-----------------|----------|-----------------|-----------|",
        ]
    )
    for row in summary_rows:
        lines.append(
            f"| {row['model']} | {row['task_id']} | {row['method']} | {row['strip_level']} | "
            f"{row['all_generated_n']} | {row['all_generated_detector_accuracy']} | "
            f"{row['all_generated_behavioral_pass_rate']} | {row['all_generated_ambiguous_rate']} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
