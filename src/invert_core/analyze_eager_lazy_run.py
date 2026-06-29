from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from invert_core.analyze_run import (
    F11_MAX_AMBIGUOUS,
    F11_MIN_ACCURACY,
    F13_MIN_VALID_N,
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
from invert_core.detectors.eager_lazy import (
    detect_eager_lazy,
    is_genuine_eager,
    is_genuine_lazy,
    pole_manipulation_success,
)
from invert_core.eager_lazy_behavioral import run_eager_lazy_behavioral_oracle
from invert_core.eager_lazy_tasks import EagerLazyTask, load_eager_lazy_tasks
from invert_core.pilot_config import CoreV2PilotConfig


def _load_tasks_by_id(tasks_file: Path) -> dict[str, EagerLazyTask]:
    return {t.task_id: t for t in load_eager_lazy_tasks(tasks_file)}


def _list_csv(values: list[str]) -> str:
    return ";".join(values)


def _detection_fields(*, include_manipulation: bool = False) -> list[str]:
    fields = [
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
        "calls_before_first_request",
        "calls_during_first_request",
        "unrequested_features_computed",
        "computed_features_before_request",
        "computed_features_on_demand",
        "trace",
        "reason",
    ]
    if include_manipulation:
        fields.extend(
            [
                "genuine_eager",
                "genuine_lazy",
                "pole_manipulation_success",
            ]
        )
    return fields


def _full_demand_fields() -> list[str]:
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
        "calls_before_first_request",
        "calls_during_first_request",
        "calls_during_second_request",
        "calls_during_third_request",
        "computed_features_before_request",
        "trace",
        "reason",
    ]


def _row_from_detection(
    *,
    run_name: str,
    art: dict[str, Any],
    strip_level: str,
    parsed: bool,
    behavioral_pass: bool,
    valid_artifact: bool,
    result: Any,
    include_manipulation: bool,
) -> dict[str, Any]:
    predicted = result.method
    true_method = art["method"]
    ev = result.evidence
    row: dict[str, Any] = {
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
        "detector_correct": _bool_str(predicted == true_method),
        "ambiguous": _bool_str(predicted == "ambiguous"),
        "calls_before_first_request": str(ev.get("calls_before_first_request", 0)),
        "calls_during_first_request": str(ev.get("calls_during_first_request", 0)),
        "unrequested_features_computed": _bool_str(bool(ev.get("unrequested_features_computed"))),
        "computed_features_before_request": _list_csv(ev.get("computed_features_before_request", [])),
        "computed_features_on_demand": _list_csv(ev.get("computed_features_on_demand", [])),
        "trace": json.dumps(ev.get("trace", [])),
        "reason": ev.get("reason", ""),
    }
    if include_manipulation:
        row["genuine_eager"] = _bool_str(is_genuine_eager(ev))
        row["genuine_lazy"] = _bool_str(is_genuine_lazy(ev))
        row["pole_manipulation_success"] = _bool_str(pole_manipulation_success(true_method, ev))
    if "calls_during_second_request" in ev:
        row["calls_during_second_request"] = str(ev.get("calls_during_second_request", 0))
        row["calls_during_third_request"] = str(ev.get("calls_during_third_request", 0))
    return row


def _accuracy(rows: list[dict[str, Any]], *, strip_level: str = "raw") -> float | None:
    subset = [
        r
        for r in rows
        if r["strip_level"] == strip_level and r.get("valid_artifact") == "true"
    ]
    if not subset:
        return None
    correct = sum(1 for r in subset if r.get("detector_correct") == "true")
    return correct / len(subset)


def _ambiguous_rate(rows: list[dict[str, Any]], *, strip_level: str = "raw") -> float | None:
    subset = [
        r
        for r in rows
        if r["strip_level"] == strip_level and r.get("valid_artifact") == "true"
    ]
    if not subset:
        return None
    amb = sum(1 for r in subset if r.get("ambiguous") == "true")
    return amb / len(subset)


def _manipulation_rate(
    rows: list[dict[str, Any]],
    *,
    requested_method: str,
    strip_level: str = "raw",
) -> float | None:
    subset = [
        r
        for r in rows
        if (
            r["strip_level"] == strip_level
            and r.get("valid_artifact") == "true"
            and r.get("method") == requested_method
        )
    ]
    if not subset:
        return None
    ok = sum(1 for r in subset if r.get("pole_manipulation_success") == "true")
    return ok / len(subset)


def _genuine_pole_accuracy(
    rows: list[dict[str, Any]],
    *,
    requested_method: str,
    strip_level: str = "raw",
) -> tuple[float | None, int]:
    if requested_method == "eager":
        flag = "genuine_eager"
    else:
        flag = "genuine_lazy"
    subset = [
        r
        for r in rows
        if (
            r["strip_level"] == strip_level
            and r.get("valid_artifact") == "true"
            and r.get("method") == requested_method
            and r.get(flag) == "true"
        )
    ]
    if not subset:
        return None, 0
    correct = sum(1 for r in subset if r.get("detector_correct") == "true")
    return correct / len(subset), len(subset)


def run_eager_lazy_analyze_run(
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
        tasks_file = project_root / "data" / "core_v2" / "tasks" / "eager_lazy_tasks.json"
        strip_levels = meta.get(
            "strip_levels",
            ["raw", "no_comments", "renamed", "no_imports", "format_normalized"],
        )
    elif config_path is not None:
        pilot = CoreV2PilotConfig.from_yaml(config_path, project_root)
        tasks_file = pilot.tasks_file
        strip_levels = pilot.strip_levels
    else:
        tasks_file = project_root / "data" / "core_v2" / "tasks" / "eager_lazy_tasks.json"
        strip_levels = ["raw", "no_comments", "renamed", "no_imports", "format_normalized"]

    tasks_by_id = _load_tasks_by_id(tasks_file)
    artifacts = _iter_code_artifacts(run_name, data_root)

    detection_rows: list[dict[str, Any]] = []
    full_demand_rows: list[dict[str, Any]] = []
    behavioral_cache: dict[str, Any] = {}

    for art in artifacts:
        code_path: Path = art["code_path"]
        task = tasks_by_id.get(art["task_id"])
        cache_key = str(code_path)
        if cache_key not in behavioral_cache:
            if task and code_path.exists():
                behavioral_cache[cache_key] = run_eager_lazy_behavioral_oracle(
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
            code = _read_code(code_path, stripped_path, strip_level, dimension="eager_vs_lazy")
            if not code.strip():
                continue

            partial_result = detect_eager_lazy(code, task=task, demand_pattern="partial")
            detection_rows.append(
                _row_from_detection(
                    run_name=run_name,
                    art=art,
                    strip_level=strip_level,
                    parsed=parsed,
                    behavioral_pass=behavioral_pass,
                    valid_artifact=valid_artifact,
                    result=partial_result,
                    include_manipulation=True,
                )
            )

            full_result = detect_eager_lazy(code, task=task, demand_pattern="full")
            full_demand_rows.append(
                _row_from_detection(
                    run_name=run_name,
                    art=art,
                    strip_level=strip_level,
                    parsed=parsed,
                    behavioral_pass=behavioral_pass,
                    valid_artifact=valid_artifact,
                    result=full_result,
                    include_manipulation=False,
                )
            )

    summary_rows = _build_all_generated_summary(detection_rows)
    valid_summary_rows = _build_valid_only_summary(detection_rows)
    stats = _compute_stats(detection_rows, artifacts)

    control_stats = {
        "partial_valid_accuracy_raw": _accuracy(detection_rows, strip_level="raw"),
        "partial_valid_accuracy_format_normalized": _accuracy(
            detection_rows, strip_level="format_normalized"
        ),
        "full_valid_accuracy_raw": _accuracy(full_demand_rows, strip_level="raw"),
        "full_valid_accuracy_format_normalized": _accuracy(
            full_demand_rows, strip_level="format_normalized"
        ),
        "partial_valid_ambiguous_rate_raw": _ambiguous_rate(detection_rows, strip_level="raw"),
        "full_valid_ambiguous_rate_raw": _ambiguous_rate(full_demand_rows, strip_level="raw"),
        "eager_manipulation_rate_raw": _manipulation_rate(
            detection_rows, requested_method="eager", strip_level="raw"
        ),
        "lazy_manipulation_rate_raw": _manipulation_rate(
            detection_rows, requested_method="lazy", strip_level="raw"
        ),
    }
    gen_eager_acc, gen_eager_n = _genuine_pole_accuracy(
        detection_rows, requested_method="eager", strip_level="raw"
    )
    gen_lazy_acc, gen_lazy_n = _genuine_pole_accuracy(
        detection_rows, requested_method="lazy", strip_level="raw"
    )
    control_stats["genuine_eager_recovery_raw"] = gen_eager_acc
    control_stats["genuine_eager_n_raw"] = gen_eager_n
    control_stats["genuine_lazy_recovery_raw"] = gen_lazy_acc
    control_stats["genuine_lazy_n_raw"] = gen_lazy_n

    detection_path = results_dir / "eager_lazy_detection.csv"
    summary_path = results_dir / "eager_lazy_summary.csv"
    valid_summary_path = results_dir / "eager_lazy_valid_only_summary.csv"
    report_path = results_dir / "eager_lazy_report.md"
    full_demand_csv = results_dir / "eager_lazy_full_demand_control.csv"
    full_demand_md = results_dir / "eager_lazy_full_demand_control.md"

    _write_csv(detection_path, _detection_fields(include_manipulation=True), detection_rows)
    _write_csv(summary_path, _all_generated_summary_fields(), summary_rows)
    _write_csv(valid_summary_path, _valid_only_summary_fields(), valid_summary_rows)
    _write_csv(full_demand_csv, _full_demand_fields(), full_demand_rows)
    _write_full_demand_control_report(
        full_demand_md,
        run_name,
        full_demand_rows,
        control_stats,
    )
    _write_eager_lazy_report(
        report_path,
        run_name,
        stats,
        summary_rows,
        valid_summary_rows,
        detection_rows,
        full_demand_rows,
        control_stats,
    )

    return RunAnalysisResult(
        detection_rows=detection_rows,
        summary_rows=summary_rows,
        valid_summary_rows=valid_summary_rows,
        report_path=report_path,
        detection_path=detection_path,
        summary_path=summary_path,
        valid_summary_path=valid_summary_path,
        stats={**stats, "control": control_stats},
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


def _f13_survival_for_model(detection_rows: list[dict[str, Any]], model: str) -> dict[str, Any]:
    raw = _aggregate_model_strip_valid(detection_rows, model, "raw")
    fmt = _aggregate_model_strip_valid(detection_rows, model, "format_normalized")
    valid_n = raw["valid_n"]
    survives = (
        valid_n >= F13_MIN_VALID_N
        and raw["valid_detector_accuracy"] is not None
        and raw["valid_detector_accuracy"] >= F11_MIN_ACCURACY
        and fmt["valid_detector_accuracy"] is not None
        and fmt["valid_detector_accuracy"] >= F11_MIN_ACCURACY
        and raw["valid_ambiguous_rate"] is not None
        and raw["valid_ambiguous_rate"] <= F11_MAX_AMBIGUOUS
        and fmt["valid_ambiguous_rate"] is not None
        and fmt["valid_ambiguous_rate"] <= F11_MAX_AMBIGUOUS
    )
    return {
        "valid_n_raw": valid_n,
        "raw_accuracy": raw["valid_detector_accuracy"],
        "format_normalized_accuracy": fmt["valid_detector_accuracy"],
        "raw_ambiguous_rate": raw["valid_ambiguous_rate"],
        "format_normalized_ambiguous_rate": fmt["valid_ambiguous_rate"],
        "survives": survives,
    }


def _write_full_demand_control_report(
    path: Path,
    run_name: str,
    full_demand_rows: list[dict[str, Any]],
    control_stats: dict[str, Any],
) -> None:
    lines = [
        f"# INVERT Core v2 — F1.3 Full-Demand Control (`{run_name}`)",
        "",
        "Validity control: all getters (`get_feature_a/b/c`) are requested before classification. "
        "When no avoidable unrequested computation remains, lazy timing signatures should collapse "
        "and overall recovery should drop relative to partial demand.",
        "",
        "## Recovery comparison (valid artifacts only)",
        "",
        "| condition | strip_level | valid_detector_accuracy | valid_ambiguous_rate |",
        "|-----------|-------------|-------------------------|----------------------|",
        f"| partial demand | raw | {_format_rate(control_stats.get('partial_valid_accuracy_raw'))} | "
        f"{_format_rate(control_stats.get('partial_valid_ambiguous_rate_raw'))} |",
        f"| partial demand | format_normalized | "
        f"{_format_rate(control_stats.get('partial_valid_accuracy_format_normalized'))} | — |",
        f"| full demand control | raw | {_format_rate(control_stats.get('full_valid_accuracy_raw'))} | "
        f"{_format_rate(control_stats.get('full_valid_ambiguous_rate_raw'))} |",
        f"| full demand control | format_normalized | "
        f"{_format_rate(control_stats.get('full_valid_accuracy_format_normalized'))} | — |",
        "",
        "## Interpretation",
        "",
    ]
    partial_acc = control_stats.get("partial_valid_accuracy_raw")
    full_acc = control_stats.get("full_valid_accuracy_raw")
    if partial_acc is not None and full_acc is not None and full_acc < partial_acc:
        lines.append(
            "- **Control passed (directional):** full-demand recovery is lower than partial-demand, "
            "consistent with discrimination relying on avoidable unrequested computation."
        )
    elif partial_acc is not None and full_acc is not None:
        lines.append(
            "- **Review:** full-demand recovery did not fall below partial-demand on this run; "
            "inspect per-model rows in `eager_lazy_full_demand_control.csv`."
        )
    else:
        lines.append("- Insufficient valid artifacts to compare partial vs full demand.")

    lines.extend(
        [
            "",
            "## Per-method full-demand outcomes (raw, valid artifacts)",
            "",
            "| requested method | valid_n | detector_accuracy | ambiguous_rate |",
            "|------------------|---------|-------------------|----------------|",
        ]
    )
    for method in ("eager", "lazy"):
        subset = [
            r
            for r in full_demand_rows
            if r["strip_level"] == "raw"
            and r.get("valid_artifact") == "true"
            and r.get("method") == method
        ]
        if not subset:
            lines.append(f"| {method} | 0 | — | — |")
            continue
        acc = sum(1 for r in subset if r.get("detector_correct") == "true") / len(subset)
        amb = sum(1 for r in subset if r.get("ambiguous") == "true") / len(subset)
        lines.append(f"| {method} | {len(subset)} | {_format_rate(acc)} | {_format_rate(amb)} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_eager_lazy_report(
    path: Path,
    run_name: str,
    stats: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    valid_summary_rows: list[dict[str, Any]],
    detection_rows: list[dict[str, Any]],
    full_demand_rows: list[dict[str, Any]],
    control_stats: dict[str, Any],
) -> None:
    models = sorted({r["model"] for r in detection_rows})
    model_f13 = {model: _f13_survival_for_model(detection_rows, model) for model in models}

    model_rankings = _build_model_rankings(detection_rows, model_f13)
    for row in model_rankings:
        row["f1_3_survives"] = model_f13.get(row["model"], {}).get("survives", False)

    conclusions = _sweep_conclusions(
        [{**r, "f1_1_survives": r.get("f1_3_survives", False)} for r in model_rankings]
    )

    def _f13_answer(model_key: str, f13: dict[str, Any]) -> str:
        if model_key not in models:
            return f"**No data** for {_model_display_name(model_key)} in this run."
        if f13.get("survives"):
            return (
                f"**Yes.** {_model_display_name(model_key)} meets preregistered F1.3 thresholds "
                f"on valid artifacts (valid_n={f13.get('valid_n_raw')}, "
                f"raw accuracy={_format_rate(f13.get('raw_accuracy'))}, "
                f"format_normalized accuracy={_format_rate(f13.get('format_normalized_accuracy'))}, "
                f"ambiguous rate={_format_rate(f13.get('raw_ambiguous_rate'))})."
            )
        return (
            f"**No / not yet.** {_model_display_name(model_key)} does not meet all F1.3 thresholds "
            f"(valid_n={f13.get('valid_n_raw', 0)}, "
            f"raw accuracy={_format_rate(f13.get('raw_accuracy'))}, "
            f"format_normalized accuracy={_format_rate(f13.get('format_normalized_accuracy'))}, "
            f"ambiguous rate={_format_rate(f13.get('raw_ambiguous_rate'))})."
        )

    gen_eager_acc = control_stats.get("genuine_eager_recovery_raw")
    gen_lazy_acc = control_stats.get("genuine_lazy_recovery_raw")
    gen_eager_n = control_stats.get("genuine_eager_n_raw", 0)
    gen_lazy_n = control_stats.get("genuine_lazy_n_raw", 0)

    lines = [
        f"# INVERT Core v2 — F1.3 Eager/Lazy Report (`{run_name}`)",
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
            "## 2. Normal partial-demand recovery",
            "",
            "Detector requests only `get_feature_a` before classification (primary F1.3 condition).",
            "",
            "| strip_level | valid_detector_accuracy | valid_ambiguous_rate |",
            "|-------------|-------------------------|----------------------|",
            f"| raw | {_format_rate(control_stats.get('partial_valid_accuracy_raw'))} | "
            f"{_format_rate(control_stats.get('partial_valid_ambiguous_rate_raw'))} |",
            f"| format_normalized | "
            f"{_format_rate(control_stats.get('partial_valid_accuracy_format_normalized'))} | — |",
            "",
            "## 3. Full-demand control recovery",
            "",
            "All getters requested before classification (`eager_lazy_full_demand_control.csv`). "
            "Lazy pole should become largely non-recoverable when no avoidable computation remains.",
            "",
            "| strip_level | valid_detector_accuracy | valid_ambiguous_rate |",
            "|-------------|-------------------------|----------------------|",
            f"| raw | {_format_rate(control_stats.get('full_valid_accuracy_raw'))} | "
            f"{_format_rate(control_stats.get('full_valid_ambiguous_rate_raw'))} |",
            f"| format_normalized | "
            f"{_format_rate(control_stats.get('full_valid_accuracy_format_normalized'))} | — |",
            "",
            "## 4. Per-pole manipulation success (partial demand, valid artifacts, raw)",
            "",
            "| requested method | manipulation_success_rate | rule |",
            "|------------------|---------------------------|------|",
            f"| eager | {_format_rate(control_stats.get('eager_manipulation_rate_raw'))} | "
            "all features computed before first getter |",
            f"| lazy | {_format_rate(control_stats.get('lazy_manipulation_rate_raw'))} | "
            "no unrequested feature computed before/during first getter |",
            "",
            "## 5. Recovery conditioned on genuine poles (partial demand, raw)",
            "",
            "| requested method | genuine_n | detector_accuracy |",
            "|------------------|-----------|-------------------|",
            f"| eager (genuine eager only) | {gen_eager_n} | {_format_rate(gen_eager_acc)} |",
            f"| lazy (genuine lazy only) | {gen_lazy_n} | {_format_rate(gen_lazy_acc)} |",
            "",
            "## 6. Model ranking (valid-only partial-demand recovery)",
            "",
            "| rank | model | generated_n | valid_n | valid_artifact_rate | "
            "valid_accuracy_raw | valid_accuracy_format_normalized | "
            "valid_ambiguous_rate_raw | f1_3_survives |",
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
            f"{'pass' if row.get('f1_3_survives') else 'fail'} |"
        )

    lines.extend(
        [
            "",
            "## 7. Local model conclusions",
            "",
            "### Models supporting F1.3",
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
            "## 8. Recovery on valid artifacts only (partial demand)",
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
            "## 9. F1.3 decision (per model, partial demand)",
            "",
            f"Preregistered rule: valid_n >= {F13_MIN_VALID_N}, valid_detector_accuracy >= "
            f"{F11_MIN_ACCURACY} at raw and format_normalized, valid_ambiguous_rate <= "
            f"{F11_MAX_AMBIGUOUS}.",
            "",
        ]
    )
    for row in model_rankings:
        f13 = model_f13.get(row["model"], {})
        lines.extend(
            [
                f"### {_model_display_name(row['model'])}",
                "",
                _f13_answer(row["model"], f13),
                "",
            ]
        )

    lines.extend(
        [
            "### Should invalid artifacts be interpreted as recovery failure?",
            "",
            "**No.** Invalid artifacts failed behavioral validation (parse/runtime/correctness). "
            "They are manipulation/validity failures and must not enter valid-only recovery metrics.",
            "",
            "### Process signature vs mathematical identity",
            "",
            "Eager and lazy variants compute the same feature formulas; only the timing of "
            "callback invocation differs. Successful F1.3 recovery therefore supports "
            "dynamic temporal process signatures beyond static arithmetic identity.",
            "",
            "## 10. All-generated summary (includes invalid artifacts)",
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
