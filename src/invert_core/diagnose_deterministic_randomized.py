from __future__ import annotations

import ast
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from invert_core.analyze_run import _bool_str, _iter_code_artifacts, _write_csv
from invert_core.deterministic_randomized_behavioral import (
    DeterministicRandomizedBehavioralResult,
    run_deterministic_randomized_behavioral_oracle,
)
from invert_core.deterministic_randomized_tasks import (
    DeterministicRandomizedTask,
    load_deterministic_randomized_tasks,
)

FAILURE_CATEGORIES = [
    "missing_class_ItemProcessor",
    "wrong_constructor_signature",
    "missing_process_all",
    "visit_fn_not_called",
    "visit_fn_called_wrong_number_of_times",
    "output_not_expected_set",
    "exception_during_execution",
    "demo_code_or_print_side_effect",
    "seed_not_supported",
    "other",
]

DIAGNOSIS_FIELDS = [
    "run",
    "model",
    "task_id",
    "method",
    "rep",
    "path",
    "parsed",
    "behavioral_pass",
    "failure_category",
    "short_failure_reason",
    "oracle_error",
    "captures_visit_fn_return_value",
    "has_print",
    "has_main_guard",
    "signature_excerpt",
]

_CAPTURE_VISIT_FN_RETURN = re.compile(
    r"(=\s*(?:self\.)?(?:visit_fn|process_fn)\s*\("
    r"|\[\s*(?:self\.)?(?:visit_fn|process_fn)\s*\("
    r"|\.append\s*\(\s*(?:self\.)?(?:visit_fn|process_fn)\s*\("
    r"|\.add\s*\(\s*(?:self\.)?(?:visit_fn|process_fn)\s*\()",
    re.MULTILINE,
)


@dataclass
class DiagnoseDeterministicRandomizedResult:
    rows: list[dict[str, Any]] = field(default_factory=list)
    csv_path: Path | None = None
    md_path: Path | None = None


def _item_processor_class_node(code: str) -> ast.ClassDef | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "ItemProcessor":
            return node
    return None


def _signature_excerpt(code: str, *, max_lines: int = 14) -> str:
    cls = _item_processor_class_node(code)
    if cls is None:
        lines = [line.rstrip() for line in code.strip().splitlines() if line.strip()]
        return "\n".join(lines[:max_lines])
    parts: list[str] = [f"class {cls.name}:"]
    for node in cls.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            try:
                segment = ast.get_source_segment(code, node)
                if segment:
                    parts.append(segment)
                else:
                    args = ", ".join(a.arg for a in node.args.args)
                    parts.append(f"    def {node.name}({args}): ...")
            except Exception:
                args = ", ".join(a.arg for a in node.args.args)
                parts.append(f"    def {node.name}({args}): ...")
        if sum(1 for p in parts if p.startswith("    def ")) >= 2:
            break
    text = "\n".join(parts)
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines] + ["..."])


def _code_flags(code: str) -> dict[str, bool]:
    return {
        "captures_visit_fn_return_value": bool(_CAPTURE_VISIT_FN_RETURN.search(code)),
        "has_print": "print(" in code,
        "has_main_guard": '__name__ == "__main__"' in code or "__main__" in code,
    }


def classify_behavioral_failure(
    code: str,
    result: DeterministicRandomizedBehavioralResult,
    *,
    task: DeterministicRandomizedTask,
) -> tuple[str, str]:
    flags = _code_flags(code)
    err = result.error or ""

    if flags["has_print"] or flags["has_main_guard"]:
        return (
            "demo_code_or_print_side_effect",
            "Generated code includes print statements or demo/main guard.",
        )

    if err == "no_item_processor_class" or err == "wrong_class_name":
        return ("missing_class_ItemProcessor", err)

    if err == "constructor_signature_mismatch":
        if "seed" in code and "def __init__" in code and "seed" not in _init_param_names(code):
            return ("seed_not_supported", "Constructor does not accept seed=None.")
        return ("wrong_constructor_signature", err)

    if err == "missing_process_all":
        return ("missing_process_all", err)

    if err == "visit_fn_not_called_exactly_once_per_item":
        return (
            "visit_fn_called_wrong_number_of_times",
            "visit_fn was not invoked exactly once per expected item.",
        )

    if err == "extra_or_missing_visit_fn_calls":
        return ("visit_fn_not_called", "visit_fn calls do not cover the expected item set.")

    if err.startswith("runtime_error:"):
        if flags["captures_visit_fn_return_value"]:
            return (
                "exception_during_execution",
                "Runtime failure after treating visit_fn(item) as a transforming function "
                f"(oracle: {err.removeprefix('runtime_error: ').strip()}).",
            )
        return ("exception_during_execution", err.removeprefix("runtime_error: ").strip())

    if err in {"invalid_return_type", "wrong_output_set"}:
        if flags["captures_visit_fn_return_value"]:
            return (
                "output_not_expected_set",
                "Returns values collected from visit_fn(item) instead of the original input "
                "items; visit_fn is a void side-effect callback.",
            )
        return ("output_not_expected_set", err)

    if err.startswith("exec_failed:"):
        return ("exception_during_execution", err.removeprefix("exec_failed: ").strip())

    if err.startswith("instantiation_failed:"):
        return ("exception_during_execution", err.removeprefix("instantiation_failed: ").strip())

    if result.behavioral_pass:
        return ("other", "behavioral oracle passed unexpectedly")

    return ("other", err or "unknown behavioral failure")


def _init_param_names(code: str) -> set[str]:
    cls = _item_processor_class_node(code)
    if cls is None:
        return set()
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            return {a.arg for a in node.args.args}
    return set()


def run_diagnose_deterministic_randomized(
    run_name: str,
    project_root: Path,
) -> DiagnoseDeterministicRandomizedResult:
    data_root = project_root / "data" / "core_v2"
    results_dir = project_root / "results" / "core_v2" / "runs" / run_name
    results_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = project_root / "data" / "core_v2" / "tasks" / "deterministic_randomized_tasks.json"
    tasks_by_id = {
        t.task_id: t for t in load_deterministic_randomized_tasks(tasks_file)
    }
    artifacts = _iter_code_artifacts(run_name, data_root)

    diagnosis_rows: list[dict[str, Any]] = []
    for art in sorted(
        artifacts,
        key=lambda a: (a["model"], a["task_id"], a["method"], a["rep"]),
    ):
        task = tasks_by_id[art["task_id"]]
        code_path: Path = art["code_path"]
        code = code_path.read_text(encoding="utf-8") if code_path.exists() else ""
        behavioral = run_deterministic_randomized_behavioral_oracle(code, task)
        category, reason = classify_behavioral_failure(code, behavioral, task=task)
        flags = _code_flags(code)

        diagnosis_rows.append(
            {
                "run": run_name,
                "model": art["model"],
                "task_id": art["task_id"],
                "method": art["method"],
                "rep": str(art["rep"]),
                "path": str(code_path),
                "parsed": _bool_str(behavioral.parsed),
                "behavioral_pass": _bool_str(behavioral.behavioral_pass),
                "failure_category": category if not behavioral.behavioral_pass else "",
                "short_failure_reason": reason if not behavioral.behavioral_pass else "",
                "oracle_error": behavioral.error or "",
                "captures_visit_fn_return_value": _bool_str(
                    flags["captures_visit_fn_return_value"]
                ),
                "has_print": _bool_str(flags["has_print"]),
                "has_main_guard": _bool_str(flags["has_main_guard"]),
                "signature_excerpt": _signature_excerpt(code),
            }
        )

    csv_path = results_dir / "deterministic_randomized_diagnosis.csv"
    md_path = results_dir / "deterministic_randomized_diagnosis.md"
    _write_csv(csv_path, DIAGNOSIS_FIELDS, diagnosis_rows)
    _write_diagnosis_report(md_path, run_name, diagnosis_rows)

    return DiagnoseDeterministicRandomizedResult(
        rows=diagnosis_rows,
        csv_path=csv_path,
        md_path=md_path,
    )


def _write_diagnosis_report(
    path: Path,
    run_name: str,
    rows: list[dict[str, Any]],
) -> None:
    n = len(rows)
    parsed = sum(1 for r in rows if r["parsed"] == "true")
    passed = sum(1 for r in rows if r["behavioral_pass"] == "true")

    by_model: dict[str, Counter[str]] = defaultdict(Counter)
    by_method: dict[str, Counter[str]] = defaultdict(Counter)
    categories = Counter(
        r["failure_category"] for r in rows if r["behavioral_pass"] != "true"
    )
    capture_count = sum(
        1 for r in rows if r["captures_visit_fn_return_value"] == "true"
    )

    for row in rows:
        if row["behavioral_pass"] == "true":
            continue
        cat = row["failure_category"] or "other"
        by_model[row["model"]][cat] += 1
        by_method[row["method"]][cat] += 1

    top5 = categories.most_common(5)

    if capture_count == n and passed == 0:
        verdict = (
            "**Prompt/API-contract failure (systematic).** Every artifact defines "
            "`ItemProcessor` with the expected class name and constructor, calls "
            "`visit_fn` once per item, but treats `visit_fn(item)` as a **map/transform** "
            "returning processed values. The benchmark contract requires `visit_fn` to be a "
            "void side-effect callback; `process_all()` must return the original input items "
            "(set or sorted list), not callback return values."
        )
    elif passed == 0:
        verdict = (
            "**Mixed generation failure.** Artifacts parse but fail behavioral validity for "
            "multiple distinct reasons; inspect per-category counts below."
        )
    else:
        verdict = "**Partial validity.** Some artifacts pass behavioral checks."

    lines = [
        f"# Deterministic/Randomized pilot diagnosis (`{run_name}`)",
        "",
        "## Summary",
        "",
        f"- Generated artifacts inspected: **{n}**",
        f"- Parsed (`ItemProcessor` loads): **{parsed}**",
        f"- Behavioral pass: **{passed}**",
        f"- Behavioral fail: **{n - passed}**",
        f"- Artifacts capturing `visit_fn(...)` return value: **{capture_count}**",
        "",
        "## Verdict",
        "",
        verdict,
        "",
        "## Top failure modes",
        "",
        "| rank | failure_category | count |",
        "|------|------------------|-------|",
    ]
    for idx, (cat, count) in enumerate(top5, start=1):
        lines.append(f"| {idx} | `{cat}` | {count} |")

    lines.extend(["", "## Failures by model", ""])
    for model in sorted(by_model):
        total = sum(by_model[model].values())
        breakdown = ", ".join(f"{cat}={cnt}" for cat, cnt in sorted(by_model[model].items()))
        lines.append(f"- `{model}`: **{total}** fails ({breakdown})")

    lines.extend(["", "## Failures by requested method", ""])
    for method in sorted(by_method):
        total = sum(by_method[method].values())
        breakdown = ", ".join(f"{cat}={cnt}" for cat, cnt in sorted(by_method[method].items()))
        lines.append(f"- `{method}`: **{total}** fails ({breakdown})")

    lines.extend(
        [
            "",
            "## Representative failure mechanism",
            "",
            "Typical generated pattern (deterministic example):",
            "",
            "```python",
            "processed_item = self.visit_fn(item)",
            "processed_items.append(processed_item)",
            "return sorted(processed_items)  # wrong: accumulates callback return values",
            "```",
            "",
            "Expected contract:",
            "",
            "```python",
            "self.visit_fn(item)  # side effect only; ignore return value",
            "return sorted(self.items)  # or set(self.items)",
            "```",
            "",
            "## Notes",
            "",
            "- `parsed=true` for all failing artifacts: class loads and constructor accepts "
            "`(items, visit_fn, seed=None)`.",
            "- Ordering/randomization logic is often present but unvalidated because behavioral "
            "validity fails first on return-value handling.",
            "- Detector ambiguity follows from invalid outputs (`None` sets) or runtime exceptions "
            "during repeated trace collection.",
            "",
            "See `deterministic_randomized_diagnosis.csv` for per-artifact excerpts.",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
