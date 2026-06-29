from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from invert_core.behavioral import run_behavioral_oracle
from invert_core.detectors.integration import detect_integration
from invert_core.ode_tasks import OdeTask, load_ode_tasks
from invert_core.pilot_config import CoreV2PilotConfig
from invert_core.stripping import StripLevel, strip_code


@dataclass
class RunAnalysisResult:
    detection_rows: list[dict[str, Any]] = field(default_factory=list)
    summary_rows: list[dict[str, Any]] = field(default_factory=list)
    report_path: Path | None = None
    detection_path: Path | None = None
    summary_path: Path | None = None
    stats: dict[str, Any] = field(default_factory=dict)


def _integration_entry(strip_level: str) -> str | None:
    if strip_level in ("raw", "no_comments"):
        return "integrate_ode"
    return None


def _load_tasks_by_id(tasks_file: Path) -> dict[str, OdeTask]:
    return {t.task_id: t for t in load_ode_tasks(tasks_file)}


def _iter_code_artifacts(run_name: str, data_root: Path) -> list[dict[str, Any]]:
    code_root = data_root / "code" / run_name
    if not code_root.exists():
        return []
    artifacts: list[dict[str, Any]] = []
    for code_path in sorted(code_root.rglob("rep_*.py")):
        parts = code_path.relative_to(code_root).parts
        if len(parts) != 4:
            continue
        model, task_id, method, rep_file = parts
        rep = int(rep_file.replace("rep_", "").replace(".py", ""))
        raw_path = data_root / "raw" / run_name / model / task_id / method / f"rep_{rep}.json"
        artifacts.append(
            {
                "code_path": code_path,
                "raw_path": raw_path,
                "model": model,
                "task_id": task_id,
                "method": method,
                "rep": rep,
            }
        )
    return artifacts


def _read_code(code_path: Path, stripped_path: Path, strip_level: str) -> str:
    if strip_level == "raw" and code_path.exists():
        return code_path.read_text(encoding="utf-8")
    if stripped_path.exists():
        return stripped_path.read_text(encoding="utf-8")
    if code_path.exists():
        code = code_path.read_text(encoding="utf-8")
        if strip_level == "raw":
            return code
        return strip_code(code, StripLevel(strip_level))
    return ""


def run_analyze_run(
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
        tasks_file = project_root / "data" / "core_v2" / "tasks" / "euler_rk4_tasks.json"
        strip_levels = meta.get(
            "strip_levels",
            ["raw", "no_comments", "renamed", "no_imports", "format_normalized"],
        )
    elif config_path is not None:
        pilot = CoreV2PilotConfig.from_yaml(config_path, project_root)
        tasks_file = pilot.tasks_file
        strip_levels = pilot.strip_levels
    else:
        tasks_file = project_root / "data" / "core_v2" / "tasks" / "euler_rk4_tasks.json"
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
                behavioral_cache[cache_key] = run_behavioral_oracle(
                    code_path.read_text(encoding="utf-8"), task
                )
            else:
                behavioral_cache[cache_key] = None
        behavioral = behavioral_cache[cache_key]

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

            result = detect_integration(code, entry_function=_integration_entry(strip_level))
            predicted = result.method
            true_method = art["method"]
            correct = predicted == true_method
            parsed = behavioral.parsed if behavioral else False
            behavioral_pass = behavioral.behavioral_pass if behavioral else False
            manipulation_success = behavioral.manipulation_success if behavioral else False

            detection_rows.append(
                {
                    "run_name": run_name,
                    "model": art["model"],
                    "task_id": art["task_id"],
                    "method": true_method,
                    "rep": art["rep"],
                    "strip_level": strip_level,
                    "predicted_label": predicted,
                    "true_label": true_method,
                    "correct": str(correct).lower(),
                    "parsed": str(parsed).lower(),
                    "behavioral_pass": str(behavioral_pass).lower(),
                    "manipulation_success": str(manipulation_success).lower(),
                    "ambiguous": str(predicted == "ambiguous").lower(),
                    "derivative_calls_per_step": result.evidence.get(
                        "derivative_calls_per_step", ""
                    ),
                    "rk4_weighted_combination": result.evidence.get(
                        "rk4_weighted_combination", ""
                    ),
                }
            )

    summary_rows = _build_summary(detection_rows)
    stats = _compute_stats(detection_rows, artifacts)

    detection_path = results_dir / "integration_detection.csv"
    summary_path = results_dir / "integration_summary.csv"
    report_path = results_dir / "integration_report.md"

    _write_csv(detection_path, _detection_fields(), detection_rows)
    _write_csv(summary_path, _summary_fields(), summary_rows)
    _write_report(report_path, run_name, stats, summary_rows, detection_rows)

    return RunAnalysisResult(
        detection_rows=detection_rows,
        summary_rows=summary_rows,
        report_path=report_path,
        detection_path=detection_path,
        summary_path=summary_path,
        stats=stats,
    )


def _detection_fields() -> list[str]:
    return [
        "run_name",
        "model",
        "task_id",
        "method",
        "rep",
        "strip_level",
        "predicted_label",
        "true_label",
        "correct",
        "parsed",
        "behavioral_pass",
        "manipulation_success",
        "ambiguous",
        "derivative_calls_per_step",
        "rk4_weighted_combination",
    ]


def _summary_fields() -> list[str]:
    return [
        "model",
        "task_id",
        "method",
        "strip_level",
        "n",
        "detector_accuracy",
        "manipulation_success_rate",
        "ambiguous_rate",
        "behavioral_pass_rate",
    ]


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def _build_summary(detection_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in detection_rows:
        key = (row["model"], row["task_id"], row["method"], row["strip_level"])
        groups[key].append(row)

    summary: list[dict[str, Any]] = []
    for (model, task_id, method, strip_level), rows in sorted(groups.items()):
        n = len(rows)
        acc = sum(1 for r in rows if r["correct"] == "true") / n if n else 0.0
        manip = sum(1 for r in rows if r["manipulation_success"] == "true") / n if n else 0.0
        amb = sum(1 for r in rows if r["ambiguous"] == "true") / n if n else 0.0
        beh = sum(1 for r in rows if r["behavioral_pass"] == "true") / n if n else 0.0
        summary.append(
            {
                "model": model,
                "task_id": task_id,
                "method": method,
                "strip_level": strip_level,
                "n": str(n),
                "detector_accuracy": f"{acc:.4f}",
                "manipulation_success_rate": f"{manip:.4f}",
                "ambiguous_rate": f"{amb:.4f}",
                "behavioral_pass_rate": f"{beh:.4f}",
            }
        )
    return summary


def _compute_stats(
    detection_rows: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    raw_rows = [r for r in detection_rows if r["strip_level"] == "raw"]
    parsed = sum(1 for r in raw_rows if r["parsed"] == "true")
    euler = sum(1 for r in raw_rows if r["predicted_label"] == "euler")
    rk4 = sum(1 for r in raw_rows if r["predicted_label"] == "rk4")
    ambiguous = sum(1 for r in raw_rows if r["predicted_label"] == "ambiguous")
    return {
        "n_artifacts": len(artifacts),
        "n_detection_rows": len(detection_rows),
        "n_parsed": parsed,
        "n_euler": euler,
        "n_rk4": rk4,
        "n_ambiguous": ambiguous,
        "raw_detector_accuracy": (
            sum(1 for r in raw_rows if r["correct"] == "true") / len(raw_rows)
            if raw_rows
            else 0.0
        ),
    }


def _strip_level_accuracy(summary_rows: list[dict[str, Any]], strip_level: str) -> float | None:
    rows = [r for r in summary_rows if r["strip_level"] == strip_level]
    if not rows:
        return None
    accs = [float(r["detector_accuracy"]) for r in rows]
    return sum(accs) / len(accs)


def _write_report(
    path: Path,
    run_name: str,
    stats: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    detection_rows: list[dict[str, Any]],
) -> None:
    strip_levels = sorted({r["strip_level"] for r in summary_rows})
    level_lines: list[str] = []
    destroy_signal: list[str] = []
    for level in strip_levels:
        acc = _strip_level_accuracy(summary_rows, level)
        if acc is None:
            continue
        level_lines.append(f"- `{level}`: mean detector accuracy = {acc:.3f}")
        if acc < 0.90 and level != "raw":
            destroy_signal.append(level)

    failures: dict[str, list[str]] = defaultdict(list)
    for row in detection_rows:
        if row["strip_level"] != "raw":
            continue
        if row["manipulation_success"] != "true" or row["correct"] != "true":
            key = f"{row['model']}/{row['task_id']}/{row['method']}"
            detail = []
            if row["manipulation_success"] != "true":
                detail.append("behavioral_fail")
            if row["correct"] != "true":
                detail.append(f"detector={row['predicted_label']}")
            failures[key].append(f"rep_{row['rep']}({','.join(detail)})")

    n = stats["n_artifacts"]
    justify = (
        "**Not yet.** Run the full 36-artifact pilot and confirm ≥0.90 detector accuracy "
        "across strip levels with acceptable manipulation success before adding quadrature."
        if n < 36
        else "**Maybe.** Review per-task/model failures below; quadrature should wait until "
        "F1.1 signal is stable on generated artifacts."
    )

    lines = [
        f"# INVERT Core v2 — F1.1 Integration Report (`{run_name}`)",
        "",
        "## Artifact counts",
        "",
        f"- Generated artifacts found: **{stats['n_artifacts']}**",
        f"- Parsed (behavioral load): **{stats['n_parsed']}** (raw level)",
        f"- Classified euler / rk4 / ambiguous (raw): **{stats['n_euler']}** / "
        f"**{stats['n_rk4']}** / **{stats['n_ambiguous']}**",
        f"- Raw-level detector accuracy: **{stats['raw_detector_accuracy']:.3f}**",
        "",
        "## Detector accuracy after stripping",
        "",
    ]
    if level_lines:
        lines.extend(level_lines)
    else:
        lines.append("- No stripped artifacts analyzed yet.")

    lines.extend(
        [
            "",
            "## Strip levels that weaken F1.1 signal",
            "",
        ]
    )
    if destroy_signal:
        lines.append(
            "Mean accuracy dropped below 0.90 at: "
            + ", ".join(f"`{level}`" for level in destroy_signal)
        )
    else:
        lines.append(
            "No strip level in this run dropped mean detector accuracy below 0.90 "
            "(or insufficient data)."
        )

    lines.extend(["", "## Model/task manipulation failures (raw level)", ""])
    if failures:
        for key, reps in sorted(failures.items()):
            lines.append(f"- `{key}`: {', '.join(reps)}")
    else:
        lines.append("- None observed on raw level (or no artifacts).")

    lines.extend(
        [
            "",
            "## Is this enough to justify quadrature next?",
            "",
            justify,
            "",
            "## Summary table",
            "",
            "| model | task | method | strip_level | n | accuracy | manipulation | ambiguous |",
            "|-------|------|--------|-------------|---|----------|--------------|-----------|",
        ]
    )
    for row in summary_rows:
        lines.append(
            f"| {row['model']} | {row['task_id']} | {row['method']} | {row['strip_level']} | "
            f"{row['n']} | {row['detector_accuracy']} | {row['manipulation_success_rate']} | "
            f"{row['ambiguous_rate']} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
