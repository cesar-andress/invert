from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntegrationEvidence:
    derivative_calls_per_step: int
    rk4_weighted_combination: bool
    integration_loops: int
    step_update_nodes: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class IntegrationResult:
    method: str  # euler | rk4 | ambiguous
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"method": self.method, "evidence": self.evidence}


_RK4_WEIGHT_PATTERN = re.compile(
    r"(\*\s*2|\*\s*0\.5|/\s*6|/\s*6\.0|1\s*/\s*6|2\s*/\s*6|1\s*/\s*3)"
)


def _unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _is_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def _call_target_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _count_calls_in_body(body: list[ast.stmt], target_names: set[str] | None = None) -> dict[str, int]:
    counts: dict[str, int] = {}

    class Counter(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:
            name = _call_target_name(node)
            if name and (target_names is None or name in target_names):
                counts[name] = counts.get(name, 0) + 1
            self.generic_visit(node)

    for stmt in body:
        Counter().visit(stmt)
    return counts


def _infer_derivative_names(tree: ast.AST) -> set[str]:
    """Names called repeatedly inside loops — likely derivative evaluations."""
    loop_call_counts: dict[str, int] = {}

    for node in ast.walk(tree):
        if not isinstance(node, (ast.For, ast.While)):
            continue
        body = node.body
        counts = _count_calls_in_body(body)
        for name, n in counts.items():
            if n >= 1:
                loop_call_counts[name] = max(loop_call_counts.get(name, 0), n)

    if not loop_call_counts:
        counts = _count_calls_in_body(
            [s for s in tree.body if isinstance(s, ast.stmt)]  # type: ignore[attr-defined]
            if isinstance(tree, ast.Module)
            else [],
        )
        loop_call_counts = counts

    candidates = {n for n, c in loop_call_counts.items() if c >= 1}
    common = {"f", "deriv", "derivative", "rhs", "dydt", "func"}
    matched = candidates & common
    if matched:
        return matched
    if loop_call_counts:
        max_count = max(loop_call_counts.values())
        return {n for n, c in loop_call_counts.items() if c == max_count}
    return set()


def _body_has_rk4_weighted_combination(body: list[ast.stmt]) -> bool:
    text = "\n".join(_unparse(s) for s in body)
    has_weight = bool(re.search(r"/\s*6|/\s*6\.0|\*\s*2\b", text))
    call_count = 0
    for stmt in body:
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call):
                call_count += 1
    return has_weight and call_count >= 4


def _max_derivative_calls_per_step(tree: ast.AST, deriv_names: set[str]) -> tuple[int, int]:
    max_calls = 0
    loop_count = 0

    for node in ast.walk(tree):
        if not isinstance(node, (ast.For, ast.While)):
            continue
        loop_count += 1
        counts = _count_calls_in_body(node.body, deriv_names if deriv_names else None)
        step_calls = sum(counts.values()) if deriv_names else sum(counts.values())
        if not deriv_names:
            step_calls = sum(counts.values())
        else:
            step_calls = sum(counts.get(n, 0) for n in deriv_names)
        max_calls = max(max_calls, step_calls)

    if loop_count == 0:
        counts = _count_calls_in_body(
            [n for n in tree.body if isinstance(n, ast.stmt)]  # type: ignore[attr-defined]
            if isinstance(tree, ast.Module)
            else [],
            deriv_names if deriv_names else None,
        )
        step_calls = sum(counts.values())
        max_calls = max(max_calls, step_calls)

    return max_calls, loop_count


def detect_integration(code: str, *, entry_function: str | None = None) -> IntegrationResult:
    """Detect Euler vs RK4 from auditable process signature in code."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return IntegrationResult(
            method="ambiguous",
            evidence={"error": f"syntax_error: {exc}", "derivative_calls_per_step": 0},
        )

    if entry_function:
        func_nodes = [
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name == entry_function
        ]
        if func_nodes:
            tree = func_nodes[0]

    deriv_names = _infer_derivative_names(tree)
    max_calls, loop_count = _max_derivative_calls_per_step(tree, deriv_names)

    rk4_weighted = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            if _body_has_rk4_weighted_combination(node.body):
                rk4_weighted = True
                break

    if not rk4_weighted and isinstance(tree, ast.FunctionDef):
        rk4_weighted = _body_has_rk4_weighted_combination(tree.body)

    evidence = IntegrationEvidence(
        derivative_calls_per_step=max_calls,
        rk4_weighted_combination=rk4_weighted,
        integration_loops=loop_count,
        step_update_nodes=sorted(deriv_names),
        notes=[],
    )

    if max_calls >= 4 and rk4_weighted:
        method = "rk4"
        evidence.notes.append("Four derivative evaluations with RK4 weighted-combination pattern")
    elif max_calls == 1 and not rk4_weighted:
        method = "euler"
        evidence.notes.append("Single derivative evaluation per step without RK4 combination")
    elif max_calls >= 4:
        method = "rk4"
        evidence.notes.append("Four derivative evaluations per step")
    elif max_calls == 1:
        method = "euler"
        evidence.notes.append("Single derivative evaluation per step")
    else:
        method = "ambiguous"
        evidence.notes.append(
            f"Ambiguous signature: {max_calls} derivative calls/step, rk4_pattern={rk4_weighted}"
        )

    return IntegrationResult(
        method=method,
        evidence={
            "derivative_calls_per_step": evidence.derivative_calls_per_step,
            "rk4_weighted_combination": evidence.rk4_weighted_combination,
            "integration_loops": evidence.integration_loops,
            "derivative_names": evidence.step_update_nodes,
            "notes": evidence.notes,
        },
    )


def detect_integration_file(path: str, *, entry_function: str | None = None) -> IntegrationResult:
    from pathlib import Path

    code = Path(path).read_text(encoding="utf-8")
    return detect_integration(code, entry_function=entry_function)
