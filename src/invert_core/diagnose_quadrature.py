from __future__ import annotations

import ast
import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from invert_core.analyze_quadrature_run import _quadrature_entry
from invert_core.analyze_run import _iter_code_artifacts, _read_code, _write_csv
from invert_core.detectors.quadrature import detect_quadrature, diagnose_trapezoidal_pattern_family

FAILURE_CLASSES = [
    "detector_too_strict",
    "nonstandard_valid_trapezoidal",
    "not_trapezoidal",
    "stripping_broke_detector",
    "ambiguous_legitimate",
]

DIAGNOSIS_FIELDS = [
    "run",
    "model",
    "task_id",
    "method",
    "rep",
    "strip_level",
    "path",
    "detected_method",
    "detector_evidence",
    "valid_artifact",
    "behavioral_pass",
    "has_endpoint_averaging",
    "has_h_times_pattern",
    "has_loop_accumulation",
    "has_explicit_fa_fb_div2",
    "has_init_total_fa_plus_fb",
    "has_divide_by_2_at_end",
    "has_n_plus_1_points",
    "pattern_family",
    "failure_classification",
    "classification_notes",
    "code_excerpt",
]


@dataclass
class DiagnoseQuadratureResult:
    rows: list[dict[str, Any]] = field(default_factory=list)
    csv_path: Path | None = None
    md_path: Path | None = None


def _bool_str(value: bool) -> str:
    return "true" if value else "false"


def _artifact_key(model: str, task_id: str, rep: int | str) -> tuple[str, str, str]:
    return (model, task_id, str(rep))


def _resolve_entry(strip_level: str) -> str | None:
    return _quadrature_entry(strip_level)


def _integrate_function_node(code: str, entry_function: str | None) -> ast.FunctionDef | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    if entry_function:
        for fn in funcs:
            if fn.name == entry_function:
                return fn
    if len(funcs) == 1:
        return funcs[0]
    for fn in funcs:
        params = [a.arg for a in fn.args.args]
        if len(params) >= 4 and params[0] in {"f", "x0", "x1"}:
            return fn
    return funcs[0] if funcs else None


def _function_text(code: str, entry_function: str | None) -> str:
    fn = _integrate_function_node(code, entry_function)
    if fn is None:
        return code
    try:
        segment = ast.get_source_segment(code, fn)
        if segment:
            return segment
    except Exception:
        pass
    try:
        return ast.unparse(fn)
    except Exception:
        return code


def _code_excerpt(code: str, entry_function: str | None, *, max_lines: int = 12) -> str:
    text = _function_text(code, entry_function).strip()
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines] + ["..."])


def analyze_trapezoidal_code_patterns(
    code: str,
    *,
    entry_function: str | None = None,
) -> dict[str, bool]:
    text = _function_text(code, entry_function)

    endpoint_averaging = bool(
        re.search(
            r"0\.5\s*\*\s*\(\s*\w+\([^)]*\)\s*\+\s*\w+\([^)]*\)\s*\)",
            text,
        )
        or re.search(
            r"0\.5\s*\(\s*\w+\([^)]*\)\s*\+\s*\w+\([^)]*\)\s*\)",
            text,
        )
        or re.search(
            r"0\.5\s*\*\s*\(\s*\w+\[[^\]]+\]\s*\+\s*\w+\[[^\]]+\]\s*\)",
            text,
        )
    )
    explicit_fa_fb_div2 = bool(
        re.search(r"\(\s*\w+\([^)]*\)\s*\+\s*\w+\([^)]*\)\s*\)\s*/\s*2", text)
        or re.search(r"\(\s*\w+\[[^\]]+\]\s*\+\s*\w+\[[^\]]+\]\s*\)\s*/\s*2", text)
    )
    init_total_fa_plus_fb = bool(
        re.search(
            r"=\s*(?!0\.5\s*\()\s*\w+\([^)]*\)\s*\+\s*\w+\([^)]*\)",
            text,
        )
        or re.search(
            r"=\s*(?!0\.5\s*\()\s*\w+\[[^\]]+\]\s*\+\s*\w+\[[^\]]+\]",
            text,
        )
    )
    h_times_pattern = bool(
        re.search(r"\*\s*h\b|h\s*\*|\*\=\s*h\b", text)
        or re.search(r"return\s+[^;\n]*\*\s*\w+", text)
        or re.search(r"\*\=\s*\w+", text)
    )
    step_var_match = re.search(r"(\w+)\s*=\s*\([^)]+\)\s*/\s*(\w+)", text)
    return_scale_match = re.search(r"return\s+\w+\s*\*\s*(\w+)", text)
    if step_var_match and return_scale_match:
        if step_var_match.group(1) == return_scale_match.group(1):
            h_times_pattern = True
    loop_accumulation = bool(
        re.search(r"for\s+\w+\s+in\s+[^:]+:", text) and "+=" in text
    )
    divide_by_2_at_end = bool(re.search(r"return\s+[^;\n]+/\s*2\b", text))
    n_plus_1_points = bool(
        re.search(r"range\s*\(\s*n\s*\+\s*1\s*\)", text)
        or re.search(r"range\s*\(\s*0\s*,\s*n\s*\+\s*1\s*\)", text)
        or re.search(r"range\s*\(\s*1\s*,\s*n\s*\+\s*1\s*\)", text)
        or re.search(r"for\s+\w+\s+in\s+range\s*\(\s*n\s*\+\s*1\s*\)", text)
    )

    return {
        "has_endpoint_averaging": endpoint_averaging,
        "has_h_times_pattern": h_times_pattern,
        "has_loop_accumulation": loop_accumulation,
        "has_explicit_fa_fb_div2": explicit_fa_fb_div2,
        "has_init_total_fa_plus_fb": init_total_fa_plus_fb,
        "has_divide_by_2_at_end": divide_by_2_at_end,
        "has_n_plus_1_points": n_plus_1_points,
    }


def _looks_like_trapezoidal(patterns: dict[str, bool]) -> bool:
    endpoint = (
        patterns["has_endpoint_averaging"]
        or patterns["has_explicit_fa_fb_div2"]
        or patterns["has_init_total_fa_plus_fb"]
    )
    scaling = patterns["has_h_times_pattern"] or patterns["has_divide_by_2_at_end"]
    return endpoint and scaling and patterns["has_loop_accumulation"]


def _looks_nonstandard_trapezoidal(patterns: dict[str, bool]) -> bool:
    if not patterns["has_loop_accumulation"]:
        return False
    return (
        patterns["has_n_plus_1_points"]
        or patterns["has_init_total_fa_plus_fb"]
        or patterns["has_divide_by_2_at_end"]
        or (
            patterns["has_endpoint_averaging"]
            and patterns["has_h_times_pattern"]
            and not patterns["has_explicit_fa_fb_div2"]
        )
    )


def _integrate_body_suggests_simpson(code: str, entry_function: str | None) -> bool:
    text = _function_text(code, entry_function)
    has_4 = bool(re.search(r"\*\s*4|\b4\s*\*", text))
    has_2 = bool(re.search(r"(?<![\d.])\*\s*2\b|\b2\s*\*(?!\s*\*)", text))
    has_h3 = bool(re.search(r"/\s*3\b|/\s*3\.0", text))
    return has_4 and has_2 and has_h3


def _stripping_regression(
    strip_level: str,
    detections_by_level: dict[str, str],
    patterns: dict[str, bool],
    *,
    detected_method: str,
) -> bool:
    if strip_level in ("raw", "no_comments"):
        return False
    current = detections_by_level.get(strip_level, detected_method)
    raw = detections_by_level.get("raw", "")
    no_comments = detections_by_level.get("no_comments", "")
    if raw == "trapezoidal" and current != "trapezoidal":
        return True
    if no_comments == "trapezoidal" and current != "trapezoidal":
        return True
    if current == "simpson" and raw in {"trapezoidal", "ambiguous"}:
        return True
    if current != "trapezoidal" and _looks_like_trapezoidal(patterns):
        return True
    return False


def classify_trapezoidal_failure(
    *,
    strip_level: str,
    detected_method: str,
    behavioral_pass: bool,
    patterns: dict[str, bool],
    detections_by_level: dict[str, str],
    code: str,
    entry_function: str | None,
) -> tuple[str, str]:
    if _stripping_regression(
        strip_level,
        detections_by_level,
        patterns,
        detected_method=detected_method,
    ):
        return (
            "stripping_broke_detector",
            "Detection regressed after stripping or entry-function scope changed.",
        )

    simpson_body = _integrate_body_suggests_simpson(code, entry_function)
    if simpson_body and detected_method == "simpson":
        return (
            "not_trapezoidal",
            "Integrate body matches Simpson 4/2 with h/3 scaling.",
        )

    if not behavioral_pass and not _looks_like_trapezoidal(patterns):
        return (
            "not_trapezoidal",
            "Behavioral oracle failed and code lacks trapezoidal weight signatures.",
        )

    if behavioral_pass and _looks_like_trapezoidal(patterns) and detected_method != "trapezoidal":
        notes = "Valid trapezoidal structure present; detector missed combined-endpoint or *= h patterns."
        if patterns["has_endpoint_averaging"] and not patterns["has_explicit_fa_fb_div2"]:
            notes = (
                "Uses 0.5*(f(a)+f(b)) endpoint averaging; detector expects separate half weights."
            )
        if patterns["has_h_times_pattern"] and "return" not in _function_text(code, entry_function):
            notes += " Final scaling uses *= h rather than return ... * h."
        return ("detector_too_strict", notes)

    if behavioral_pass and _looks_nonstandard_trapezoidal(patterns) and detected_method != "trapezoidal":
        if patterns["has_n_plus_1_points"] or (
            patterns["has_h_times_pattern"]
            and "*= h" not in code
            and "return" in _function_text(code, entry_function)
            and "* h" not in _function_text(code, entry_function)
        ):
            return (
                "nonstandard_valid_trapezoidal",
                "Behavioral pass with unconventional trapezoidal layout (indexing, n+1 grid, or late scaling).",
            )

    if detected_method == "ambiguous" and behavioral_pass:
        return (
            "ambiguous_legitimate",
            "Behavioral pass but arithmetic signatures are mixed or partially obscured.",
        )

    if detected_method == "simpson" and behavioral_pass and _looks_like_trapezoidal(patterns):
        return (
            "detector_too_strict",
            "Trapezoidal code misread as Simpson due to unrelated numeric literals or full-module scan.",
        )

    return (
        "ambiguous_legitimate",
        "Insufficient trapezoidal signatures to override ambiguous/wrong detector output.",
    )


def _code_path_for_row(
    data_root: Path,
    run_name: str,
    model: str,
    task_id: str,
    method: str,
    rep: int,
    strip_level: str,
    code_path: Path,
) -> Path:
    stripped_path = (
        data_root
        / "stripped"
        / run_name
        / strip_level
        / model
        / task_id
        / method
        / f"rep_{rep}.py"
    )
    if strip_level == "raw":
        return code_path
    if stripped_path.exists():
        return stripped_path
    return code_path


def _load_detection_rows(detection_csv: Path) -> list[dict[str, str]]:
    if not detection_csv.exists():
        return []
    with open(detection_csv, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _build_detection_index(
    rows: list[dict[str, str]],
) -> dict[tuple[str, str, str], dict[str, str]]:
    index: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        if row.get("method") != "trapezoidal":
            continue
        key = _artifact_key(row["model"], row["task_id"], row["rep"])
        index.setdefault(key, {})[row["strip_level"]] = row.get("detected_method", "")
    return index


def run_diagnose_quadrature(run_name: str, project_root: Path) -> DiagnoseQuadratureResult:
    data_root = project_root / "data" / "core_v2"
    results_dir = project_root / "results" / "core_v2" / "runs" / run_name
    results_dir.mkdir(parents=True, exist_ok=True)

    detection_csv = results_dir / "quadrature_detection.csv"
    detection_rows = _load_detection_rows(detection_csv)
    detection_index = _build_detection_index(detection_rows)

    failed_rows = [
        r
        for r in detection_rows
        if r.get("method") == "trapezoidal" and r.get("detector_correct") == "false"
    ]

    artifacts = {
        _artifact_key(a["model"], a["task_id"], a["rep"]): a
        for a in _iter_code_artifacts(run_name, data_root)
    }

    diagnosis_rows: list[dict[str, Any]] = []

    for row in failed_rows:
        model = row["model"]
        task_id = row["task_id"]
        rep = int(row["rep"])
        strip_level = row["strip_level"]
        art = artifacts.get(_artifact_key(model, task_id, rep))
        if art is None:
            continue

        code_path = art["code_path"]
        stripped_path = _code_path_for_row(
            data_root, run_name, model, task_id, "trapezoidal", rep, strip_level, code_path
        )
        code = _read_code(code_path, stripped_path, strip_level)
        if not code.strip():
            continue

        entry_function = _resolve_entry(strip_level)
        result = detect_quadrature(code, entry_function=entry_function)
        patterns = analyze_trapezoidal_code_patterns(code, entry_function=entry_function)
        detections_by_level = detection_index.get(_artifact_key(model, task_id, rep), {})
        failure_class, notes = classify_trapezoidal_failure(
            strip_level=strip_level,
            detected_method=result.method,
            behavioral_pass=row.get("behavioral_pass") == "true",
            patterns=patterns,
            detections_by_level=detections_by_level,
            code=code,
            entry_function=entry_function,
        )
        if result.method == "trapezoidal" and row.get("detector_correct") == "false":
            failure_class = "detector_too_strict"
            notes = (
                "Historical run marked incorrect/ambiguous; live detector now classifies trapezoidal."
            )

        pattern_family = diagnose_trapezoidal_pattern_family(code, entry_function=entry_function)

        diagnosis_rows.append(
            {
                "run": run_name,
                "model": model,
                "task_id": task_id,
                "method": row["method"],
                "rep": str(rep),
                "strip_level": strip_level,
                "path": str(stripped_path if stripped_path.exists() else code_path),
                "detected_method": result.method,
                "detector_evidence": json.dumps(result.evidence, sort_keys=True),
                "valid_artifact": row.get("valid_artifact", ""),
                "behavioral_pass": row.get("behavioral_pass", ""),
                "has_endpoint_averaging": _bool_str(patterns["has_endpoint_averaging"]),
                "has_h_times_pattern": _bool_str(patterns["has_h_times_pattern"]),
                "has_loop_accumulation": _bool_str(patterns["has_loop_accumulation"]),
                "has_explicit_fa_fb_div2": _bool_str(patterns["has_explicit_fa_fb_div2"]),
                "has_init_total_fa_plus_fb": _bool_str(patterns["has_init_total_fa_plus_fb"]),
                "has_divide_by_2_at_end": _bool_str(patterns["has_divide_by_2_at_end"]),
                "has_n_plus_1_points": _bool_str(patterns["has_n_plus_1_points"]),
                "pattern_family": pattern_family,
                "failure_classification": failure_class,
                "classification_notes": notes,
                "code_excerpt": _code_excerpt(code, entry_function),
            }
        )

    csv_path = results_dir / "quadrature_diagnosis.csv"
    md_path = results_dir / "quadrature_diagnosis.md"
    _write_csv(csv_path, DIAGNOSIS_FIELDS, diagnosis_rows)
    _write_diagnosis_report(md_path, run_name, diagnosis_rows)

    return DiagnoseQuadratureResult(rows=diagnosis_rows, csv_path=csv_path, md_path=md_path)


def _write_diagnosis_report(path: Path, run_name: str, rows: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = {cls: 0 for cls in FAILURE_CLASSES}
    for row in rows:
        counts[row["failure_classification"]] = counts.get(row["failure_classification"], 0) + 1

    lines = [
        f"# Quadrature detector diagnosis (`{run_name}`)",
        "",
        "Failed trapezoidal artifacts where the detector returned `ambiguous` or the wrong method.",
        "The detector itself was not modified for this report.",
        "",
        "## Failure classification counts",
        "",
    ]
    for cls in FAILURE_CLASSES:
        lines.append(f"- **{cls}**: {counts.get(cls, 0)}")

    lines.extend(["", "## Interpretation guide", ""])
    guide = {
        "detector_too_strict": (
            "Generated code appears to implement trapezoidal quadrature correctly, but rigid "
            "signature rules (separate half weights, return * h) missed it."
        ),
        "nonstandard_valid_trapezoidal": (
            "Behaviorally valid trapezoidal implementations using unconventional structure "
            "(n+1 sample grid, indexed arrays, late *= h scaling)."
        ),
        "not_trapezoidal": (
            "Code is not trapezoidal or failed the behavioral oracle without recoverable "
            "trapezoidal signatures."
        ),
        "stripping_broke_detector": (
            "Raw/no_comments detection was stronger; renaming or import stripping changed scope "
            "or introduced false Simpson cues."
        ),
        "ambiguous_legitimate": (
            "Ambiguous classification is reasonable given weak or mixed arithmetic signatures."
        ),
    }
    for cls in FAILURE_CLASSES:
        lines.append(f"### {cls}")
        lines.append("")
        lines.append(guide[cls])
        lines.append("")

    for cls in FAILURE_CLASSES:
        subset = [r for r in rows if r["failure_classification"] == cls][:5]
        if not subset:
            continue
        lines.extend([f"## Examples: {cls}", ""])
        for row in subset:
            lines.extend(
                [
                    f"### {row['model']} / {row['task_id']} / rep_{row['rep']} / {row['strip_level']}",
                    "",
                    f"- detected: `{row['detected_method']}`",
                    f"- behavioral_pass: `{row['behavioral_pass']}`",
                    f"- notes: {row['classification_notes']}",
                    "",
                    "```python",
                    row["code_excerpt"],
                    "```",
                    "",
                ]
            )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
