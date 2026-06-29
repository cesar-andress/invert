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
    _read_code,
    _sweep_conclusions,
    _write_csv,
)
from invert_core.deterministic_randomized_behavioral import (
    run_deterministic_randomized_behavioral_oracle,
)
from invert_core.deterministic_randomized_tasks import (
    DeterministicRandomizedTask,
    load_deterministic_randomized_task_file,
)
from invert_core.detectors.deterministic_randomized import (
    detect_deterministic_randomized,
    is_genuine_deterministic,
    is_genuine_randomized,
    pole_manipulation_success,
)
from invert_core.pilot_config import CoreV2PilotConfig
from invert_core.stripping import StripLevel, strip_code


def _load_tasks_by_id(tasks_file: Path) -> dict[str, DeterministicRandomizedTask]:
    task_file = load_deterministic_randomized_task_file(tasks_file)
    return {t.task_id: t for t in task_file.tasks}


def _load_fixed_seed(tasks_file: Path) -> int:
    return load_deterministic_randomized_task_file(tasks_file).fixed_seed


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
        "unique_trace_count",
        "traces",
        "reason",
    ]


def _fixed_seed_control_fields() -> list[str]:
    return [
        "run",
        "model",
        "task_id",
        "method",
        "rep",
        "strip_level",
        "detected_method",
        "ambiguous",
        "unique_trace_count",
        "traces",
        "control_collapse",
        "reason",
    ]


def _row_from_result(
    *,
    run_name: str,
    art: dict[str, Any],
    strip_level: str,
    task: DeterministicRandomizedTask,
    parsed: bool,
    behavioral_pass: bool,
    valid_artifact: bool,
    result: Any,
) -> dict[str, Any]:
    ev = result.evidence
    return {
        "run": run_name,
        "model": art["model"],
        "task_id": task.task_id,
        "method": art["method"],
        "rep": art["rep"],
        "strip_level": strip_level,
        "parsed": _bool_str(parsed),
        "behavioral_pass": _bool_str(behavioral_pass),
        "valid_artifact": _bool_str(valid_artifact),
        "detected_method": result.method,
        "detector_correct": _bool_str(result.method == art["method"]),
        "ambiguous": _bool_str(result.method == "ambiguous"),
        "unique_trace_count": str(ev.get("unique_trace_count", 0)),
        "traces": json.dumps(ev.get("traces", [])),
        "genuine_deterministic": _bool_str(is_genuine_deterministic(ev)),
        "genuine_randomized": _bool_str(is_genuine_randomized(ev)),
        "pole_manipulation_success": _bool_str(
            pole_manipulation_success(art["method"], ev)
        ),
        "reason": ev.get("reason", ""),
    }


def _fixed_seed_row(
    *,
    run_name: str,
    art: dict[str, Any],
    strip_level: str,
    result: Any,
) -> dict[str, Any]:
    ev = result.evidence
    unique = int(ev.get("unique_trace_count", 0))
    collapse = art["method"] == "randomized" and unique == 1
    return {
        "run": run_name,
        "model": art["model"],
        "task_id": art["task_id"],
        "method": art["method"],
        "rep": art["rep"],
        "strip_level": strip_level,
        "detected_method": result.method,
        "ambiguous": _bool_str(result.method == "ambiguous"),
        "unique_trace_count": str(unique),
        "traces": json.dumps(ev.get("traces", [])),
        "control_collapse": _bool_str(collapse),
        "reason": ev.get("reason", ""),
    }


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
    rows: list[dict[str, Any]], *, requested_method: str, strip_level: str = "raw"
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
    rows: list[dict[str, Any]], *, requested_method: str, strip_level: str = "raw"
) -> tuple[float | None, int]:
    flag = "genuine_deterministic" if requested_method == "deterministic" else "genuine_randomized"
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


def _randomized_collapse_rate(
    rows: list[dict[str, Any]], *, strip_level: str = "raw"
) -> float | None:
    subset = [
        r
        for r in rows
        if (
            r["strip_level"] == strip_level
            and r.get("method") == "randomized"
        )
    ]
    if not subset:
        return None
    collapsed = sum(1 for r in subset if r.get("control_collapse") == "true")
    return collapsed / len(subset)


def run_deterministic_randomized_analyze_run(
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
        tasks_file = project_root / "data" / "core_v2" / "tasks" / (
            "deterministic_randomized_tasks.json"
        )
        strip_levels = meta.get(
            "strip_levels",
            ["raw", "no_comments", "renamed", "no_imports", "format_normalized"],
        )
    elif config_path is not None:
        pilot = CoreV2PilotConfig.from_yaml(config_path, project_root)
        tasks_file = pilot.tasks_file
        strip_levels = pilot.strip_levels
    else:
        tasks_file = (
            project_root / "data" / "core_v2" / "tasks" / "deterministic_randomized_tasks.json"
        )
        strip_levels = ["raw", "no_comments", "renamed", "no_imports", "format_normalized"]

    tasks_by_id = _load_tasks_by_id(tasks_file)
    fixed_seed = _load_fixed_seed(tasks_file)
    primary_ids = {tid for tid, t in tasks_by_id.items() if t.is_primary}
    artifacts = _iter_code_artifacts(run_name, data_root)

    detection_rows: list[dict[str, Any]] = []
    fixed_seed_rows: list[dict[str, Any]] = []
    behavioral_cache: dict[str, Any] = {}

    for art in artifacts:
        if art["task_id"] not in primary_ids:
            continue
        code_path: Path = art["code_path"]
        task = tasks_by_id.get(art["task_id"])
        if task is None:
            continue
        cache_key = str(code_path)
        if cache_key not in behavioral_cache:
            if code_path.exists():
                behavioral_cache[cache_key] = run_deterministic_randomized_behavioral_oracle(
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
            code = _read_code(
                code_path,
                stripped_path,
                strip_level,
                dimension="deterministic_vs_randomized",
            )
            if not code.strip():
                continue

            primary_result = detect_deterministic_randomized(
                code, task, mode="primary"
            )
            detection_rows.append(
                _row_from_result(
                    run_name=run_name,
                    art=art,
                    strip_level=strip_level,
                    task=task,
                    parsed=parsed,
                    behavioral_pass=behavioral_pass,
                    valid_artifact=valid_artifact,
                    result=primary_result,
                )
            )

            fixed_result = detect_deterministic_randomized(
                code,
                task,
                mode="fixed_seed_control",
                fixed_seed=fixed_seed,
            )
            fixed_seed_rows.append(
                _fixed_seed_row(
                    run_name=run_name,
                    art=art,
                    strip_level=strip_level,
                    result=fixed_result,
                )
            )

    summary_rows = _build_all_generated_summary(detection_rows)
    valid_summary_rows = _build_valid_only_summary(detection_rows)
    stats = _compute_stats(
        detection_rows, [a for a in artifacts if a["task_id"] in primary_ids]
    )

    control_stats = {
        "primary_valid_accuracy_raw": _accuracy(detection_rows, strip_level="raw"),
        "primary_valid_accuracy_format_normalized": _accuracy(
            detection_rows, strip_level="format_normalized"
        ),
        "primary_valid_ambiguous_rate_raw": _ambiguous_rate(
            detection_rows, strip_level="raw"
        ),
        "deterministic_manipulation_rate_raw": _manipulation_rate(
            detection_rows, requested_method="deterministic", strip_level="raw"
        ),
        "randomized_manipulation_rate_raw": _manipulation_rate(
            detection_rows, requested_method="randomized", strip_level="raw"
        ),
        "randomized_collapse_rate_raw": _randomized_collapse_rate(
            fixed_seed_rows, strip_level="raw"
        ),
    }
    gen_det_acc, gen_det_n = _genuine_pole_accuracy(
        detection_rows, requested_method="deterministic", strip_level="raw"
    )
    gen_rand_acc, gen_rand_n = _genuine_pole_accuracy(
        detection_rows, requested_method="randomized", strip_level="raw"
    )
    control_stats["genuine_deterministic_recovery_raw"] = gen_det_acc
    control_stats["genuine_deterministic_n_raw"] = gen_det_n
    control_stats["genuine_randomized_recovery_raw"] = gen_rand_acc
    control_stats["genuine_randomized_n_raw"] = gen_rand_n

    detection_path = results_dir / "deterministic_randomized_detection.csv"
    summary_path = results_dir / "deterministic_randomized_summary.csv"
    valid_summary_path = results_dir / "deterministic_randomized_valid_only_summary.csv"
    fixed_seed_path = results_dir / "deterministic_randomized_fixed_seed_control.csv"
    report_path = results_dir / "deterministic_randomized_report.md"

    _write_csv(detection_path, _detection_fields(), detection_rows)
    _write_csv(summary_path, _all_generated_summary_fields(), summary_rows)
    _write_csv(valid_summary_path, _valid_only_summary_fields(), valid_summary_rows)
    _write_csv(fixed_seed_path, _fixed_seed_control_fields(), fixed_seed_rows)
    _write_report(
        report_path,
        run_name,
        stats,
        summary_rows,
        detection_rows,
        fixed_seed_rows,
        control_stats,
        fixed_seed=fixed_seed,
    )

    return RunAnalysisResult(
        detection_rows=detection_rows,
        summary_rows=summary_rows,
        valid_summary_rows=valid_summary_rows,
        report_path=report_path,
        detection_path=detection_path,
        summary_path=summary_path,
        valid_summary_path=valid_summary_path,
        stats={
            **stats,
            "control": control_stats,
            "fixed_seed_control_path": str(fixed_seed_path),
        },
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


def _f15_survival_for_model(detection_rows: list[dict[str, Any]], model: str) -> dict[str, Any]:
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


def _write_report(
    path: Path,
    run_name: str,
    stats: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    detection_rows: list[dict[str, Any]],
    fixed_seed_rows: list[dict[str, Any]],
    control_stats: dict[str, Any],
    *,
    fixed_seed: int,
) -> None:
    models = sorted({r["model"] for r in detection_rows})
    model_survival = {
        model: _f15_survival_for_model(detection_rows, model) for model in models
    }

    model_rankings = _build_model_rankings(detection_rows, model_survival)
    for row in model_rankings:
        row["f1_5_survives"] = model_survival.get(row["model"], {}).get("survives", False)

    conclusions = _sweep_conclusions(
        [{**r, "f1_1_survives": r.get("f1_5_survives", False)} for r in model_rankings]
    )

    gen_det_acc = control_stats.get("genuine_deterministic_recovery_raw")
    gen_rand_acc = control_stats.get("genuine_randomized_recovery_raw")
    gen_det_n = control_stats.get("genuine_deterministic_n_raw", 0)
    gen_rand_n = control_stats.get("genuine_randomized_n_raw", 0)

    lines = [
        f"# INVERT Core v2 — F1.5 Deterministic/Randomized Report (`{run_name}`)",
        "",
        "## 1. Generation validity (primary tasks)",
        "",
        f"- Generated artifacts: **{stats['n_artifacts']}**",
        f"- Parsed at raw level: **{stats['n_parsed']}**",
        f"- Valid behavioral artifacts: **{stats['n_valid']}**",
        f"- Invalid artifacts: **{stats['n_invalid']}**",
        "",
        "## 2. Primary inter-execution variability recovery",
        "",
        "Repeated `process_all()` runs with `seed=None`; classification uses trace identity only.",
        "",
        "| strip_level | valid_detector_accuracy | valid_ambiguous_rate |",
        "|-------------|-------------------------|----------------------|",
        f"| raw | {_format_rate(control_stats.get('primary_valid_accuracy_raw'))} | "
        f"{_format_rate(control_stats.get('primary_valid_ambiguous_rate_raw'))} |",
        f"| format_normalized | "
        f"{_format_rate(control_stats.get('primary_valid_accuracy_format_normalized'))} | — |",
        "",
        "## 3. Fixed-seed control collapse",
        "",
        f"Each artifact re-run {5} times with identical seed={fixed_seed} "
        "(`deterministic_randomized_fixed_seed_control.csv`). "
        "Randomized implementations should collapse to a single trace "
        "(detected as deterministic or ambiguous, not randomized).",
        "",
        f"- Randomized collapse rate (unique_trace_count == 1, raw): "
        f"**{_format_rate(control_stats.get('randomized_collapse_rate_raw'))}**",
        "",
        "## 4. Per-pole manipulation success (primary, valid artifacts, raw)",
        "",
        "| requested method | manipulation_success_rate | rule |",
        "|------------------|---------------------------|------|",
        f"| deterministic | {_format_rate(control_stats.get('deterministic_manipulation_rate_raw'))} | "
        "unique_trace_count == 1 under primary repeated runs |",
        f"| randomized | {_format_rate(control_stats.get('randomized_manipulation_rate_raw'))} | "
        "unique_trace_count >= 2 under primary repeated runs |",
        "",
        "## 5. Recovery conditioned on genuine poles (primary, raw)",
        "",
        "| requested method | genuine_n | detector_accuracy |",
        "|------------------|-----------|-------------------|",
        f"| deterministic (genuine only) | {gen_det_n} | {_format_rate(gen_det_acc)} |",
        f"| randomized (genuine only) | {gen_rand_n} | {_format_rate(gen_rand_acc)} |",
        "",
        "## 6. Model ranking (valid-only primary recovery)",
        "",
        "| rank | model | generated_n | valid_n | valid_artifact_rate | "
        "valid_accuracy_raw | valid_accuracy_format_normalized | "
        "valid_ambiguous_rate_raw | f1_5_survives |",
        "|------|-------|-------------|---------|---------------------|"
        "---------------------|--------------------------------|"
        "--------------------------|---------------|",
    ]
    for row in model_rankings:
        lines.append(
            f"| {row['rank']} | {row['display_name']} | {row['generated_n']} | {row['valid_n']} | "
            f"{_format_rate(row['valid_artifact_rate'])} | "
            f"{_format_rate(row['valid_accuracy_raw'])} | "
            f"{_format_rate(row['valid_accuracy_format_normalized'])} | "
            f"{_format_rate(row['valid_ambiguous_rate_raw'])} | "
            f"{'pass' if row.get('f1_5_survives') else 'fail'} |"
        )

    lines.extend(
        [
            "",
            "## 7. Local model conclusions",
            "",
            "### Models supporting F1.5",
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
            "## 8. F1.5 decision (per model)",
            "",
            f"Preregistered rule: valid_n >= {F13_MIN_VALID_N}, valid_detector_accuracy >= "
            f"{F11_MIN_ACCURACY} at raw and format_normalized, valid_ambiguous_rate <= "
            f"{F11_MAX_AMBIGUOUS}.",
            "",
            "### Inter-execution variability vs other signature classes",
            "",
            "Deterministic and randomized implementations return the same item set and call "
            "visit_fn once per item; only repeated-execution trace stability differs.",
            "",
            "## 9. All-generated summary",
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
