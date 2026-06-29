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

NA = "NA"

MODEL_DISPLAY_NAMES = {
    "ollama__qwen2_5-coder__32b": "Qwen2.5-coder:32b",
    "ollama__qwen3-coder__30b": "Qwen3-coder:30b",
    "ollama__qwen2_5-coder__14b": "Qwen2.5-coder:14b",
    "ollama__devstral__latest": "Devstral:latest",
    "ollama__deepseek-coder-v2__lite": "DeepSeek-coder-v2:lite",
    "openai": "openai",
    "anthropic": "anthropic",
    "local_stub": "local_stub",
}

F11_MIN_VALID_N = 12
F11_MIN_ACCURACY = 0.90
F11_MAX_AMBIGUOUS = 0.10


@dataclass
class RunAnalysisResult:
    detection_rows: list[dict[str, Any]] = field(default_factory=list)
    summary_rows: list[dict[str, Any]] = field(default_factory=list)
    valid_summary_rows: list[dict[str, Any]] = field(default_factory=list)
    report_path: Path | None = None
    detection_path: Path | None = None
    summary_path: Path | None = None
    valid_summary_path: Path | None = None
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


def _model_display_name(storage_model: str) -> str:
    return MODEL_DISPLAY_NAMES.get(storage_model, storage_model)


def _bool_str(value: bool) -> str:
    return "true" if value else "false"


def _rate(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return NA
    return f"{numerator / denominator:.4f}"


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

            result = detect_integration(code, entry_function=_integration_entry(strip_level))
            predicted = result.method
            true_method = art["method"]
            detector_correct = predicted == true_method

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
                    "derivative_calls_per_step": result.evidence.get(
                        "derivative_calls_per_step", ""
                    ),
                    "rk4_weighted_combination": result.evidence.get(
                        "rk4_weighted_combination", ""
                    ),
                }
            )

    summary_rows = _build_all_generated_summary(detection_rows)
    valid_summary_rows = _build_valid_only_summary(detection_rows)
    stats = _compute_stats(detection_rows, artifacts)

    detection_path = results_dir / "integration_detection.csv"
    summary_path = results_dir / "integration_summary.csv"
    valid_summary_path = results_dir / "integration_valid_only_summary.csv"
    report_path = results_dir / "integration_report.md"

    _write_csv(detection_path, _detection_fields(), detection_rows)
    _write_csv(summary_path, _all_generated_summary_fields(), summary_rows)
    _write_csv(valid_summary_path, _valid_only_summary_fields(), valid_summary_rows)
    _write_report(
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
        "derivative_calls_per_step",
        "rk4_weighted_combination",
    ]


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


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def _build_all_generated_summary(detection_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in detection_rows:
        key = (row["model"], row["task_id"], row["method"], row["strip_level"])
        groups[key].append(row)

    summary: list[dict[str, Any]] = []
    for (model, task_id, method, strip_level), rows in sorted(groups.items()):
        n = len(rows)
        summary.append(
            {
                "model": model,
                "task_id": task_id,
                "method": method,
                "strip_level": strip_level,
                "all_generated_n": str(n),
                "all_generated_detector_accuracy": _rate(
                    sum(1 for r in rows if r["detector_correct"] == "true"), n
                ),
                "all_generated_behavioral_pass_rate": _rate(
                    sum(1 for r in rows if r["behavioral_pass"] == "true"), n
                ),
                "all_generated_ambiguous_rate": _rate(
                    sum(1 for r in rows if r["ambiguous"] == "true"), n
                ),
            }
        )
    return summary


def _build_valid_only_summary(detection_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in detection_rows:
        if row["valid_artifact"] != "true":
            continue
        key = (row["model"], row["task_id"], row["method"], row["strip_level"])
        groups[key].append(row)

    all_keys = {
        (row["model"], row["task_id"], row["method"], row["strip_level"])
        for row in detection_rows
    }

    summary: list[dict[str, Any]] = []
    for key in sorted(all_keys):
        model, task_id, method, strip_level = key
        rows = groups.get(key, [])
        valid_n = len(rows)
        summary.append(
            {
                "model": model,
                "task_id": task_id,
                "method": method,
                "strip_level": strip_level,
                "valid_n": str(valid_n),
                "valid_detector_accuracy": _rate(
                    sum(1 for r in rows if r["detector_correct"] == "true"), valid_n
                ),
                "valid_ambiguous_rate": _rate(
                    sum(1 for r in rows if r["ambiguous"] == "true"), valid_n
                ),
            }
        )
    return summary


def _raw_artifact_rows(detection_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in detection_rows if r["strip_level"] == "raw"]


def _compute_stats(
    detection_rows: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    raw_rows = _raw_artifact_rows(detection_rows)
    n_generated = len(raw_rows)
    n_parsed = sum(1 for r in raw_rows if r["parsed"] == "true")
    n_valid = sum(1 for r in raw_rows if r["valid_artifact"] == "true")
    n_invalid = n_generated - n_valid

    invalid_by_group: dict[str, int] = defaultdict(int)
    for row in raw_rows:
        if row["valid_artifact"] != "true":
            key = f"{row['model']}/{row['task_id']}/{row['method']}"
            invalid_by_group[key] += 1

    models = sorted({r["model"] for r in raw_rows})
    model_f11: dict[str, dict[str, Any]] = {}
    for model in models:
        model_f11[model] = _f11_survival_for_model(detection_rows, model)

    return {
        "n_artifacts": len(artifacts),
        "n_generated_raw": n_generated,
        "n_parsed": n_parsed,
        "n_valid": n_valid,
        "n_invalid": n_invalid,
        "invalid_by_group": dict(sorted(invalid_by_group.items())),
        "model_f11": model_f11,
    }


def _aggregate_model_strip_valid(
    detection_rows: list[dict[str, Any]],
    model: str,
    strip_level: str,
) -> dict[str, Any]:
    rows = [
        r
        for r in detection_rows
        if r["model"] == model
        and r["strip_level"] == strip_level
        and r["valid_artifact"] == "true"
    ]
    valid_n = len(rows)
    if valid_n == 0:
        return {
            "valid_n": 0,
            "valid_detector_accuracy": None,
            "valid_ambiguous_rate": None,
        }
    correct = sum(1 for r in rows if r["detector_correct"] == "true")
    ambiguous = sum(1 for r in rows if r["ambiguous"] == "true")
    return {
        "valid_n": valid_n,
        "valid_detector_accuracy": correct / valid_n,
        "valid_ambiguous_rate": ambiguous / valid_n,
    }


def _f11_survival_for_model(detection_rows: list[dict[str, Any]], model: str) -> dict[str, Any]:
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
        "survives": survives,
    }


def _format_rate(value: float | None) -> str:
    if value is None:
        return NA
    return f"{value:.4f}"


def _model_validity_counts(
    detection_rows: list[dict[str, Any]], model: str
) -> tuple[int, int]:
    raw_rows = [
        r for r in detection_rows if r["model"] == model and r["strip_level"] == "raw"
    ]
    n_generated = len(raw_rows)
    n_valid = sum(1 for r in raw_rows if r["valid_artifact"] == "true")
    return n_generated, n_valid


def _build_model_rankings(
    detection_rows: list[dict[str, Any]],
    model_f11: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    models = sorted({r["model"] for r in detection_rows})
    rankings: list[dict[str, Any]] = []
    for model in models:
        n_generated, n_valid = _model_validity_counts(detection_rows, model)
        valid_artifact_rate = n_valid / n_generated if n_generated else None
        raw = _aggregate_model_strip_valid(detection_rows, model, "raw")
        fmt = _aggregate_model_strip_valid(detection_rows, model, "format_normalized")
        f11 = model_f11.get(model, {})
        rankings.append(
            {
                "model": model,
                "display_name": _model_display_name(model),
                "n_generated": n_generated,
                "n_valid": n_valid,
                "valid_artifact_rate": valid_artifact_rate,
                "valid_raw_accuracy": raw["valid_detector_accuracy"],
                "valid_fmt_accuracy": fmt["valid_detector_accuracy"],
                "ambiguous_rate": raw["valid_ambiguous_rate"],
                "f11_survives": bool(f11.get("survives")),
            }
        )

    def sort_key(row: dict[str, Any]) -> tuple:
        rate = row["valid_artifact_rate"]
        raw_acc = row["valid_raw_accuracy"]
        fmt_acc = row["valid_fmt_accuracy"]
        amb = row["ambiguous_rate"]
        return (
            0 if row["f11_survives"] else 1,
            -(rate if rate is not None else -1.0),
            -(raw_acc if raw_acc is not None else -1.0),
            -(fmt_acc if fmt_acc is not None else -1.0),
            amb if amb is not None else 999.0,
        )

    rankings.sort(key=sort_key)
    for idx, row in enumerate(rankings, start=1):
        row["rank"] = idx
    return rankings


def _write_report(
    path: Path,
    run_name: str,
    stats: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    valid_summary_rows: list[dict[str, Any]],
    detection_rows: list[dict[str, Any]],
) -> None:
    raw_valid_by_model: dict[str, dict[str, Any]] = {}
    fmt_valid_by_model: dict[str, dict[str, Any]] = {}
    models = sorted({r["model"] for r in detection_rows})
    for model in models:
        raw_valid_by_model[model] = _aggregate_model_strip_valid(
            detection_rows, model, "raw"
        )
        fmt_valid_by_model[model] = _aggregate_model_strip_valid(
            detection_rows, model, "format_normalized"
        )

    model_rankings = _build_model_rankings(detection_rows, stats["model_f11"])

    def _f11_answer(model_key: str, f11: dict[str, Any]) -> str:
        if model_key not in models:
            return f"**No data** for {_model_display_name(model_key)} in this run."
        if f11.get("survives"):
            return (
                f"**Yes.** {_model_display_name(model_key)} meets preregistered F1.1 thresholds "
                f"on valid artifacts (valid_n={f11.get('valid_n_raw')}, "
                f"raw accuracy={_format_rate(f11.get('raw_accuracy'))}, "
                f"format_normalized accuracy={_format_rate(f11.get('format_normalized_accuracy'))}, "
                f"ambiguous rate={_format_rate(f11.get('raw_ambiguous_rate'))})."
            )
        return (
            f"**No / not yet.** {_model_display_name(model_key)} does not meet all F1.1 thresholds "
            f"(valid_n={f11.get('valid_n_raw', 0)}, "
            f"raw accuracy={_format_rate(f11.get('raw_accuracy'))}, "
            f"format_normalized accuracy={_format_rate(f11.get('format_normalized_accuracy'))}, "
            f"ambiguous rate={_format_rate(f11.get('raw_ambiguous_rate'))})."
        )

    any_model_survives = any(
        stats["model_f11"].get(m, {}).get("survives") for m in models
    )
    n_valid = stats["n_valid"]
    n_generated = stats["n_generated_raw"]
    quadrature_answer = (
        "**Not yet.** At least one model must pass F1.1 valid-only survival thresholds "
        "with sufficient valid artifacts before adding quadrature."
        if not any_model_survives or n_valid < F11_MIN_VALID_N
        else "**Maybe.** One or more models meet valid-only F1.1 thresholds; review per-task "
        "failures and validity rates before expanding to quadrature."
    )

    lines = [
        f"# INVERT Core v2 — F1.1 Integration Report (`{run_name}`)",
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
            "and are excluded from valid-only recovery metrics (R_raw, R_stripped).",
            "",
            "## 2. Model ranking (valid-only recovery)",
            "",
            "Ranked by: F1.1 survival (pass first), then valid_artifact_rate, "
            "valid_detector_accuracy at raw, valid_detector_accuracy at format_normalized, "
            "ambiguous_rate (lower is better).",
            "",
            "| rank | model | valid_artifact_rate | valid_raw_acc | valid_fmt_acc | ambiguous_rate | F1.1 |",
            "|------|-------|---------------------|---------------|---------------|----------------|------|",
        ]
    )
    for row in model_rankings:
        lines.append(
            f"| {row['rank']} | {row['display_name']} | "
            f"{_format_rate(row['valid_artifact_rate'])} | "
            f"{_format_rate(row['valid_raw_accuracy'])} | "
            f"{_format_rate(row['valid_fmt_accuracy'])} | "
            f"{_format_rate(row['ambiguous_rate'])} | "
            f"{'pass' if row['f11_survives'] else 'fail'} |"
        )

    lines.extend(
        [
            "",
            "## 3. Recovery on valid artifacts only",
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

    lines.extend(["", "### Model aggregates (valid-only)", ""])
    for model in models:
        raw = raw_valid_by_model[model]
        fmt = fmt_valid_by_model[model]
        lines.append(f"**{_model_display_name(model)}**")
        lines.append(
            f"- raw: valid_n={raw['valid_n']}, accuracy={_format_rate(raw['valid_detector_accuracy'])}, "
            f"ambiguous={_format_rate(raw['valid_ambiguous_rate'])}"
        )
        lines.append(
            f"- format_normalized: valid_n={fmt['valid_n']}, "
            f"accuracy={_format_rate(fmt['valid_detector_accuracy'])}, "
            f"ambiguous={_format_rate(fmt['valid_ambiguous_rate'])}"
        )
        lines.append("")

    lines.extend(
        [
            "## 4. F1.1 decision",
            "",
            f"Preregistered rule: valid_n >= {F11_MIN_VALID_N}, valid_detector_accuracy >= "
            f"{F11_MIN_ACCURACY} at raw and format_normalized, valid_ambiguous_rate <= "
            f"{F11_MAX_AMBIGUOUS}.",
            "",
        ]
    )
    for row in model_rankings:
        f11 = stats["model_f11"].get(row["model"], {})
        lines.extend(
            [
                f"### {_model_display_name(row['model'])}",
                "",
                _f11_answer(row["model"], f11),
                "",
            ]
        )

    lines.extend(
        [
            "### Should invalid artifacts be interpreted as recovery failure?",
            "",
            "**No.** Invalid artifacts failed behavioral validation (parse/runtime/tolerance). "
            "They are manipulation/validity failures and must not enter R_raw or R_stripped.",
            "",
            "### Is this enough to move to quadrature?",
            "",
            quadrature_answer,
            "",
            "## 5. All-generated summary (includes invalid artifacts)",
            "",
            "Detector accuracy in this section includes invalid artifacts and is **not** used "
            "for F1.1 recovery decisions.",
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
