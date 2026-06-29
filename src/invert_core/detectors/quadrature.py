from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class QuadratureResult:
    method: str  # trapezoidal | simpson | ambiguous
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"method": self.method, "evidence": self.evidence}


def _unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _numeric_value(node: ast.AST) -> float | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _numeric_value(node.operand)
        return -inner if inner is not None else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _numeric_value(node.left)
        right = _numeric_value(node.right)
        if left is not None and right is not None and right != 0:
            return left / right
    return None


def _is_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call)


def _collect_coefficient_literals(tree: ast.AST) -> list[float]:
    coeffs: set[float] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mult, ast.Div)):
            for side in (node.left, node.right):
                val = _numeric_value(side)
                if val is not None and val in {0.5, 1.0, 2.0, 3.0, 4.0}:
                    coeffs.add(val)
                if isinstance(side, ast.Constant) and side.value in (2, 4):
                    coeffs.add(float(side.value))
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            if float(node.value) in {0.5, 1.0, 2.0, 3.0, 4.0}:
                coeffs.add(float(node.value))
    return sorted(coeffs)


def _body_text(tree: ast.AST) -> str:
    if isinstance(tree, ast.FunctionDef):
        return _unparse(tree)
    if isinstance(tree, ast.Module):
        return _unparse(tree)
    return _unparse(tree)


def _has_half_weight_on_call(text: str) -> bool:
    patterns = [
        r"0\.5\s*\*\s*\w+\s*\(",
        r"\w+\s*\(\s*[^)]+\)\s*\*\s*0\.5",
        r"/\s*2\s*\*\s*\w+\s*\(",
        r"\w+\s*\(\s*[^)]+\)\s*/\s*2",
        r"0\.5\s*\*",
    ]
    return any(re.search(p, text) for p in patterns)


def _has_endpoint_half_weights(tree: ast.AST, text: str) -> bool:
    half_literals = 0
    call_with_half = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            left_val = _numeric_value(node.left)
            right_val = _numeric_value(node.right)
            if left_val == 0.5 and _is_call(node.right):
                call_with_half += 1
            if right_val == 0.5 and _is_call(node.left):
                call_with_half += 1
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            if _is_call(node.left) and _numeric_value(node.right) == 2.0:
                call_with_half += 1
    if call_with_half >= 2:
        return True
    if _has_half_weight_on_call(text):
        half_literals = len(re.findall(r"0\.5|/\s*2", text))
        call_count = len(re.findall(r"\w+\s*\(", text))
        return half_literals >= 2 and call_count >= 2
    return False


def _has_simpson_4_2_pattern(tree: ast.AST, text: str) -> bool:
    has_4 = bool(re.search(r"\*\s*4|\b4\s*\*|\b4\s+if|=\s*4\b", text))
    has_2 = bool(re.search(r"(?<![\d.])\*\s*2\b|\b2\s*\*(?!\s*\*)|\belse\s+2|=\s*2\b", text))
    odd_even_branch = False
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test_text = _unparse(node.test)
            if "%" in test_text and "2" in test_text:
                odd_even_branch = True
        if isinstance(node, ast.IfExp):
            test_text = _unparse(node.test)
            if "%" in test_text and "2" in test_text:
                odd_even_branch = True
        if isinstance(node, ast.Assign):
            val_text = _unparse(node.value)
            if "4" in val_text and "2" in val_text:
                odd_even_branch = True
    weight_assign = bool(re.search(r"=\s*4\s+if|=\s*2\s+if|w\s*=\s*4|w\s*=\s*2", text))
    return (has_4 and has_2) and (odd_even_branch or weight_assign or "4 *" in text)


def _has_h_div_3(text: str) -> bool:
    return bool(
        re.search(r"\*\s*h\s*/\s*3|h\s*/\s*3|\*\s*\(\s*h\s*/\s*3|/\s*3\.0|/\s*3\b", text)
    )


def _has_final_h_multiply(text: str) -> bool:
    return bool(re.search(r"return\s+.*\*\s*h\b|return\s+.*h\s*\*", text))


def _function_eval_pattern(tree: ast.AST) -> str:
    loop_calls = 0
    endpoint_calls = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            loop_calls += sum(1 for n in ast.walk(node) if isinstance(n, ast.Call))
        if isinstance(node, ast.Call):
            endpoint_calls += 1
    if loop_calls >= 2:
        return "loop_weighted_sum"
    if endpoint_calls >= 2:
        return "endpoint_plus_samples"
    return "unknown"


def detect_quadrature(code: str, *, entry_function: str | None = None) -> QuadratureResult:
    """Detect trapezoidal vs Simpson from arithmetic weight signatures."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return QuadratureResult(
            method="ambiguous",
            evidence={
                "has_endpoint_half_weights": False,
                "has_simpson_4_2_pattern": False,
                "coefficient_literals": [],
                "function_eval_pattern": "syntax_error",
                "reason": f"syntax_error: {exc}",
            },
        )

    if entry_function:
        funcs = [
            n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == entry_function
        ]
        if funcs:
            tree = funcs[0]

    text = _body_text(tree)
    coeffs = _collect_coefficient_literals(tree)
    half_weights = _has_endpoint_half_weights(tree, text)
    simpson_42 = _has_simpson_4_2_pattern(tree, text)
    h_div_3 = _has_h_div_3(text)
    h_mult = _has_final_h_multiply(text)
    eval_pattern = _function_eval_pattern(tree)

    evidence: dict[str, Any] = {
        "has_endpoint_half_weights": half_weights,
        "has_simpson_4_2_pattern": simpson_42,
        "coefficient_literals": coeffs,
        "function_eval_pattern": eval_pattern,
        "reason": "",
    }

    if simpson_42 and h_div_3:
        evidence["reason"] = "Simpson 4/2 weight pattern with h/3 scaling"
        return QuadratureResult(method="simpson", evidence=evidence)

    if half_weights and h_mult and not h_div_3 and not simpson_42:
        evidence["reason"] = "Endpoint half weights with final h multiplication"
        return QuadratureResult(method="trapezoidal", evidence=evidence)

    if half_weights and not simpson_42 and 4.0 not in coeffs:
        evidence["reason"] = "Endpoint half weights without Simpson coefficients"
        return QuadratureResult(method="trapezoidal", evidence=evidence)

    if simpson_42 and not half_weights:
        evidence["reason"] = "4/2 interior weights detected"
        return QuadratureResult(method="simpson", evidence=evidence)

    evidence["reason"] = (
        f"Ambiguous: half_weights={half_weights}, simpson_42={simpson_42}, "
        f"h_div_3={h_div_3}, h_mult={h_mult}"
    )
    return QuadratureResult(method="ambiguous", evidence=evidence)


def detect_quadrature_file(path: str, *, entry_function: str | None = None) -> QuadratureResult:
    from pathlib import Path

    code = Path(path).read_text(encoding="utf-8")
    return detect_quadrature(code, entry_function=entry_function)
