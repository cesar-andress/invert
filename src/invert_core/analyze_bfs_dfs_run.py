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
from invert_core.bfs_dfs_behavioral import run_bfs_dfs_behavioral_oracle
from invert_core.bfs_dfs_prompts import build_bfs_dfs_stub_code
from invert_core.bfs_dfs_tasks import BfsDfsTask, load_bfs_dfs_tasks
from invert_core.detectors.bfs_dfs import (
    detect_bfs_dfs,
    is_genuine_bfs,
    is_genuine_dfs,
    pole_manipulation_success,
)
from invert_core.pilot_config import CoreV2PilotConfig
from invert_core.stripping import StripLevel, strip_code


def _load_tasks_by_id(tasks_file: Path) -> dict[str, BfsDfsTask]:
    return {t.task_id: t for t in load_bfs_dfs_tasks(tasks_file)}


def _list_csv(values: list[str]) -> str:
    return ";".join(values)


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
        "visit_trace",
        "expected_bfs_order",
        "expected_dfs_order",
        "bfs_order_match",
        "dfs_order_match",
        "genuine_bfs",
        "genuine_dfs",
        "pole_manipulation_success",
        "reason",
    ]


def _negative_control_fields() -> list[str]:
    return [
        "run",
        "task_id",
        "method",
        "strip_level",
        "detected_method",
        "ambiguous",
        "visit_trace",
        "expected_bfs_order",
        "expected_dfs_order",
        "bfs_order_match",
        "dfs_order_match",
        "reason",
    ]


def _row_from_result(
    *,
    run_name: str,
    art: dict[str, Any] | None,
    strip_level: str,
    task: BfsDfsTask,
    parsed: bool,
    behavioral_pass: bool,
    valid_artifact: bool,
    result: Any,
    include_manipulation: bool,
) -> dict[str, Any]:
    ev = result.evidence
    row: dict[str, Any] = {
        "run": run_name,
        "model": art["model"] if art else "reference_stub",
        "task_id": task.task_id,
        "method": art["method"] if art else "",
        "rep": art["rep"] if art else 0,
        "strip_level": strip_level,
        "parsed": _bool_str(parsed),
        "behavioral_pass": _bool_str(behavioral_pass),
        "valid_artifact": _bool_str(valid_artifact),
        "detected_method": result.method,
        "detector_correct": _bool_str(
            art is not None and result.method == art["method"]
        ),
        "ambiguous": _bool_str(result.method == "ambiguous"),
        "visit_trace": json.dumps(ev.get("visit_trace", [])),
        "expected_bfs_order": _list_csv(ev.get("expected_bfs_order", task.expected_bfs_order)),
        "expected_dfs_order": _list_csv(ev.get("expected_dfs_order", task.expected_dfs_order)),
        "bfs_order_match": _bool_str(bool(ev.get("bfs_order_match"))),
        "dfs_order_match": _bool_str(bool(ev.get("dfs_order_match"))),
        "reason": ev.get("reason", ""),
    }
    if include_manipulation:
        row["genuine_bfs"] = _bool_str(is_genuine_bfs(ev))
        row["genuine_dfs"] = _bool_str(is_genuine_dfs(ev))
        true_method = art["method"] if art else ""
        row["pole_manipulation_success"] = _bool_str(
            pole_manipulation_success(true_method, ev) if art else False
        )
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
    flag = "genuine_bfs" if requested_method == "bfs" else "genuine_dfs"
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


def _build_negative_control_rows(
    run_name: str,
    linear_task: BfsDfsTask,
    strip_levels: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for method in ("bfs", "dfs"):
        code = build_bfs_dfs_stub_code(linear_task, method)
        for strip_level in strip_levels:
            stripped = strip_code(code, StripLevel(strip_level), dimension="bfs_vs_dfs")
            result = detect_bfs_dfs(stripped, linear_task)
            ev = result.evidence
            rows.append(
                {
                    "run": run_name,
                    "task_id": linear_task.task_id,
                    "method": method,
                    "strip_level": strip_level,
                    "detected_method": result.method,
                    "ambiguous": _bool_str(result.method == "ambiguous"),
                    "visit_trace": json.dumps(ev.get("visit_trace", [])),
                    "expected_bfs_order": _list_csv(
                        ev.get("expected_bfs_order", linear_task.expected_bfs_order)
                    ),
                    "expected_dfs_order": _list_csv(
                        ev.get("expected_dfs_order", linear_task.expected_dfs_order)
                    ),
                    "bfs_order_match": _bool_str(bool(ev.get("bfs_order_match"))),
                    "dfs_order_match": _bool_str(bool(ev.get("dfs_order_match"))),
                    "reason": ev.get("reason", ""),
                }
            )
    return rows


def run_bfs_dfs_analyze_run(
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
        tasks_file = project_root / "data" / "core_v2" / "tasks" / "bfs_dfs_tasks.json"
        strip_levels = meta.get(
            "strip_levels",
            ["raw", "no_comments", "renamed", "no_imports", "format_normalized"],
        )
    elif config_path is not None:
        pilot = CoreV2PilotConfig.from_yaml(config_path, project_root)
        tasks_file = pilot.tasks_file
        strip_levels = pilot.strip_levels
    else:
        tasks_file = project_root / "data" / "core_v2" / "tasks" / "bfs_dfs_tasks.json"
        strip_levels = ["raw", "no_comments", "renamed", "no_imports", "format_normalized"]

    tasks_by_id = _load_tasks_by_id(tasks_file)
    linear_task = tasks_by_id.get("linear_chain")
    branching_ids = {
        tid for tid, t in tasks_by_id.items() if not t.is_negative_control
    }
    artifacts = _iter_code_artifacts(run_name, data_root)

    detection_rows: list[dict[str, Any]] = []
    behavioral_cache: dict[str, Any] = {}

    for art in artifacts:
        if art["task_id"] not in branching_ids:
            continue
        code_path: Path = art["code_path"]
        task = tasks_by_id.get(art["task_id"])
        if task is None:
            continue
        cache_key = str(code_path)
        if cache_key not in behavioral_cache:
            if code_path.exists():
                behavioral_cache[cache_key] = run_bfs_dfs_behavioral_oracle(
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
            code = _read_code(code_path, stripped_path, strip_level, dimension="bfs_vs_dfs")
            if not code.strip():
                continue

            result = detect_bfs_dfs(code, task)
            detection_rows.append(
                _row_from_result(
                    run_name=run_name,
                    art=art,
                    strip_level=strip_level,
                    task=task,
                    parsed=parsed,
                    behavioral_pass=behavioral_pass,
                    valid_artifact=valid_artifact,
                    result=result,
                    include_manipulation=True,
                )
            )

    negative_control_rows: list[dict[str, Any]] = []
    if linear_task is not None:
        negative_control_rows = _build_negative_control_rows(
            run_name, linear_task, strip_levels
        )

    summary_rows = _build_all_generated_summary(detection_rows)
    valid_summary_rows = _build_valid_only_summary(detection_rows)
    stats = _compute_stats(detection_rows, [a for a in artifacts if a["task_id"] in branching_ids])

    control_stats = {
        "primary_valid_accuracy_raw": _accuracy(detection_rows, strip_level="raw"),
        "primary_valid_accuracy_format_normalized": _accuracy(
            detection_rows, strip_level="format_normalized"
        ),
        "primary_valid_ambiguous_rate_raw": _ambiguous_rate(detection_rows, strip_level="raw"),
        "negative_control_ambiguous_rate_raw": (
            sum(1 for r in negative_control_rows if r.get("ambiguous") == "true")
            / len(negative_control_rows)
            if negative_control_rows
            else None
        ),
        "bfs_manipulation_rate_raw": _manipulation_rate(
            detection_rows, requested_method="bfs", strip_level="raw"
        ),
        "dfs_manipulation_rate_raw": _manipulation_rate(
            detection_rows, requested_method="dfs", strip_level="raw"
        ),
    }
    gen_bfs_acc, gen_bfs_n = _genuine_pole_accuracy(
        detection_rows, requested_method="bfs", strip_level="raw"
    )
    gen_dfs_acc, gen_dfs_n = _genuine_pole_accuracy(
        detection_rows, requested_method="dfs", strip_level="raw"
    )
    control_stats["genuine_bfs_recovery_raw"] = gen_bfs_acc
    control_stats["genuine_bfs_n_raw"] = gen_bfs_n
    control_stats["genuine_dfs_recovery_raw"] = gen_dfs_acc
    control_stats["genuine_dfs_n_raw"] = gen_dfs_n

    detection_path = results_dir / "bfs_dfs_detection.csv"
    summary_path = results_dir / "bfs_dfs_summary.csv"
    valid_summary_path = results_dir / "bfs_dfs_valid_only_summary.csv"
    negative_control_path = results_dir / "bfs_dfs_negative_control.csv"
    report_path = results_dir / "bfs_dfs_report.md"

    _write_csv(detection_path, _detection_fields(), detection_rows)
    _write_csv(summary_path, _all_generated_summary_fields(), summary_rows)
    _write_csv(valid_summary_path, _valid_only_summary_fields(), valid_summary_rows)
    _write_csv(negative_control_path, _negative_control_fields(), negative_control_rows)
    _write_bfs_dfs_report(
        report_path,
        run_name,
        stats,
        summary_rows,
        valid_summary_rows,
        detection_rows,
        negative_control_rows,
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


def _f14_survival_for_model(detection_rows: list[dict[str, Any]], model: str) -> dict[str, Any]:
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


def _write_bfs_dfs_report(
    path: Path,
    run_name: str,
    stats: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    valid_summary_rows: list[dict[str, Any]],
    detection_rows: list[dict[str, Any]],
    negative_control_rows: list[dict[str, Any]],
    control_stats: dict[str, Any],
) -> None:
    models = sorted({r["model"] for r in detection_rows})
    model_f14 = {model: _f14_survival_for_model(detection_rows, model) for model in models}

    model_rankings = _build_model_rankings(detection_rows, model_f14)
    for row in model_rankings:
        row["f1_4_survives"] = model_f14.get(row["model"], {}).get("survives", False)

    conclusions = _sweep_conclusions(
        [{**r, "f1_1_survives": r.get("f1_4_survives", False)} for r in model_rankings]
    )

    gen_bfs_acc = control_stats.get("genuine_bfs_recovery_raw")
    gen_dfs_acc = control_stats.get("genuine_dfs_recovery_raw")
    gen_bfs_n = control_stats.get("genuine_bfs_n_raw", 0)
    gen_dfs_n = control_stats.get("genuine_dfs_n_raw", 0)

    lines = [
        f"# INVERT Core v2 — F1.4 BFS/DFS Report (`{run_name}`)",
        "",
        "## 1. Generation validity (branching tasks)",
        "",
        f"- Generated artifacts: **{stats['n_artifacts']}**",
        f"- Parsed at raw level: **{stats['n_parsed']}**",
        f"- Valid behavioral artifacts: **{stats['n_valid']}**",
        f"- Invalid artifacts: **{stats['n_invalid']}**",
        "",
        "## 2. Primary branching-graph recovery",
        "",
        "| strip_level | valid_detector_accuracy | valid_ambiguous_rate |",
        "|-------------|-------------------------|----------------------|",
        f"| raw | {_format_rate(control_stats.get('primary_valid_accuracy_raw'))} | "
        f"{_format_rate(control_stats.get('primary_valid_ambiguous_rate_raw'))} |",
        f"| format_normalized | "
        f"{_format_rate(control_stats.get('primary_valid_accuracy_format_normalized'))} | — |",
        "",
        "## 3. Linear-chain negative control",
        "",
        "Reference stub implementations on `linear_chain` (`bfs_dfs_negative_control.csv`). "
        "BFS and DFS visit nodes in identical order; recovery should collapse to ambiguous.",
        "",
        f"- Negative-control ambiguous rate (reference stubs, all strip levels): "
        f"**{_format_rate(control_stats.get('negative_control_ambiguous_rate_raw'))}**",
        "",
        "## 4. Per-pole manipulation success (branching, valid artifacts, raw)",
        "",
        "| requested method | manipulation_success_rate | rule |",
        "|------------------|---------------------------|------|",
        f"| bfs | {_format_rate(control_stats.get('bfs_manipulation_rate_raw'))} | "
        "visit trace matches BFS order only |",
        f"| dfs | {_format_rate(control_stats.get('dfs_manipulation_rate_raw'))} | "
        "visit trace matches DFS order only |",
        "",
        "## 5. Recovery conditioned on genuine poles (branching, raw)",
        "",
        "| requested method | genuine_n | detector_accuracy |",
        "|------------------|-----------|-------------------|",
        f"| bfs (genuine BFS only) | {gen_bfs_n} | {_format_rate(gen_bfs_acc)} |",
        f"| dfs (genuine DFS only) | {gen_dfs_n} | {_format_rate(gen_dfs_acc)} |",
        "",
        "## 6. Model ranking (valid-only primary recovery)",
        "",
        "| rank | model | generated_n | valid_n | valid_artifact_rate | "
        "valid_accuracy_raw | valid_accuracy_format_normalized | "
        "valid_ambiguous_rate_raw | f1_4_survives |",
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
            f"{'pass' if row.get('f1_4_survives') else 'fail'} |"
        )

    lines.extend(
        [
            "",
            "## 7. Local model conclusions",
            "",
            "### Models supporting F1.4",
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
            "## 8. F1.4 decision (per model)",
            "",
            f"Preregistered rule: valid_n >= {F13_MIN_VALID_N}, valid_detector_accuracy >= "
            f"{F11_MIN_ACCURACY} at raw and format_normalized, valid_ambiguous_rate <= "
            f"{F11_MAX_AMBIGUOUS}.",
            "",
            "### Order signature vs mathematical identity",
            "",
            "BFS and DFS visit the same reachable set with the same number of visit_fn calls; "
            "only traversal order differs.",
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
