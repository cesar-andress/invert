from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class QuadratureResult:
    method: str  # trapezoidal | simpson | ambiguous
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"method": self.method, "evidence": self.evidence}


@dataclass
class TrapezoidalSignature:
    is_trapezoidal: bool
    step_var: str | None
    explicit_half_weights: bool
    endpoint_average: bool
    running_sum: bool
    scaled_return: bool
    has_interior_loop: bool
    has_step_scaling: bool
    pattern_family: str
    reason: str


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


def _is_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def _param_roles(fn: ast.FunctionDef) -> dict[str, str]:
    names = [arg.arg for arg in fn.args.args]
    if len(names) < 4:
        return {name: name for name in names}
    return {names[0]: "f", names[1]: "a", names[2]: "b", names[3]: "n"}


def _name_for_role(roles: dict[str, str], role: str) -> str | None:
    for name, mapped in roles.items():
        if mapped == role:
            return name
    return None


def _is_endpoint_diff(node: ast.AST, a_name: str, b_name: str) -> bool:
    if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Sub):
        return False
    return (_is_name(node.left, b_name) and _is_name(node.right, a_name)) or (
        _is_name(node.left, a_name) and _is_name(node.right, b_name)
    )


def _is_step_expr(node: ast.AST, a_name: str, b_name: str, n_name: str) -> bool:
    if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
        return False
    return _is_endpoint_diff(node.left, a_name, b_name) and _is_name(node.right, n_name)


def _find_step_var(fn: ast.FunctionDef, roles: dict[str, str]) -> str | None:
    a_name = _name_for_role(roles, "a")
    b_name = _name_for_role(roles, "b")
    n_name = _name_for_role(roles, "n")
    if not a_name or not b_name or not n_name:
        return None
    for node in fn.body:
        for child in ast.walk(node):
            if isinstance(child, ast.Assign) and len(child.targets) == 1:
                target = child.targets[0]
                if isinstance(target, ast.Name) and _is_step_expr(
                    child.value, a_name, b_name, n_name
                ):
                    return target.id
    return None


def _integrand_call_kind(node: ast.AST, roles: dict[str, str]) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    f_name = _name_for_role(roles, "f")
    if f_name is None:
        return None
    if isinstance(node.func, ast.Name):
        if node.func.id != f_name:
            return None
    else:
        return None
    if not node.args:
        return None
    arg = node.args[0]
    a_name = _name_for_role(roles, "a")
    b_name = _name_for_role(roles, "b")
    if a_name and _is_name(arg, a_name):
        return "a"
    if b_name and _is_name(arg, b_name):
        return "b"
    if _is_interior_arg(arg, roles):
        return "interior"
    return "other"


def _is_interior_arg(arg: ast.AST, roles: dict[str, str]) -> bool:
    a_name = _name_for_role(roles, "a")
    if a_name is None:
        return False
    if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
        return _is_name(arg.left, a_name) or _is_name(arg.right, a_name)
    if isinstance(arg, ast.Subscript):
        return True
    return False


def _expr_has_half_factor(expr: ast.AST) -> bool:
    val = _numeric_value(expr)
    if val == 0.5:
        return True
    if isinstance(expr, ast.BinOp):
        if isinstance(expr.op, ast.Mult):
            return _expr_has_half_factor(expr.left) or _expr_has_half_factor(expr.right)
        if isinstance(expr.op, ast.Div) and _numeric_value(expr.right) == 2.0:
            return True
    return False


def _expr_contains_half_scaling(expr: ast.AST) -> bool:
    for node in ast.walk(expr):
        if _expr_has_half_factor(node):
            return True
    return False


def _endpoint_calls_in_expr(expr: ast.AST, roles: dict[str, str]) -> set[str]:
    kinds: set[str] = set()
    for node in ast.walk(expr):
        kind = _integrand_call_kind(node, roles)
        if kind in {"a", "b"}:
            kinds.add(kind)
    return kinds


def _flatten_add(expr: ast.AST) -> list[ast.AST]:
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
        return _flatten_add(expr.left) + _flatten_add(expr.right)
    return [expr]


def _is_integrand_func_call(node: ast.AST, roles: dict[str, str]) -> bool:
    f_name = _name_for_role(roles, "f")
    return (
        isinstance(node, ast.Call)
        and f_name is not None
        and isinstance(node.func, ast.Name)
        and node.func.id == f_name
    )


def _has_explicit_half_weights(fn: ast.FunctionDef, roles: dict[str, str]) -> bool:
    half_weight_calls = 0
    for node in ast.walk(fn):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            left_half = _numeric_value(node.left) == 0.5
            right_half = _numeric_value(node.right) == 0.5
            other = node.right if left_half else node.left if right_half else None
            if other is not None and _is_integrand_func_call(other, roles):
                half_weight_calls += 1
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            if _numeric_value(node.right) == 2.0 and _is_integrand_func_call(node.left, roles):
                half_weight_calls += 1
    return half_weight_calls >= 2


def _call_uses_subscript_endpoint(arg: ast.AST) -> bool:
    if not isinstance(arg, ast.Subscript):
        return False
    sl = arg.slice
    if isinstance(sl, ast.Constant) and sl.value in (0, -1):
        return True
    if isinstance(sl, ast.UnaryOp) and isinstance(sl.op, ast.USub):
        if isinstance(sl.operand, ast.Constant) and sl.operand.value == 1:
            return True
    return False


def _is_grid_integrand_call(node: ast.AST, roles: dict[str, str]) -> bool:
    if not isinstance(node, ast.Call):
        return False
    f_name = _name_for_role(roles, "f")
    if f_name is None or not isinstance(node.func, ast.Name) or node.func.id != f_name:
        return False
    if not node.args:
        return False
    return _call_uses_subscript_endpoint(node.args[0]) or _is_interior_arg(node.args[0], roles)


def _has_combined_endpoint_half(fn: ast.FunctionDef) -> bool:
    for node in ast.walk(fn):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            half_left = _numeric_value(node.left) == 0.5
            half_right = _numeric_value(node.right) == 0.5
            other = node.right if half_left else node.left if half_right else None
            if other is None:
                continue
            if isinstance(other, ast.BinOp) and isinstance(other.op, ast.Add):
                calls = [n for n in ast.walk(other) if isinstance(n, ast.Call)]
                if len(calls) >= 2:
                    return True
    return False


def _has_endpoint_average(fn: ast.FunctionDef, roles: dict[str, str]) -> bool:
    if _has_combined_endpoint_half(fn):
        return True
    for node in ast.walk(fn):
        candidates = [node]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            candidates = _flatten_add(node)
        for sub in candidates:
            if isinstance(sub, ast.BinOp) and isinstance(sub.op, ast.Add):
                kinds = _endpoint_calls_in_expr(sub, roles)
                if kinds == {"a", "b"}:
                    if _expr_contains_half_scaling(sub):
                        return True
                    if _expr_contains_half_scaling(node):
                        return True
        if isinstance(node, ast.Assign):
            kinds = _endpoint_calls_in_expr(node.value, roles)
            if kinds == {"a", "b"} and _expr_contains_half_scaling(node.value):
                return True
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and node.value:
            kinds = _endpoint_calls_in_expr(node.value, roles)
            if kinds == {"a", "b"} and _expr_contains_half_scaling(node.value):
                return True
    return False


def _has_running_endpoint_sum(fn: ast.FunctionDef, roles: dict[str, str]) -> bool:
    endpoint_hits = 0
    for node in ast.walk(fn):
        if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Add):
            kind = _integrand_call_kind(node.value, roles)
            if kind in {"a", "b"}:
                endpoint_hits += 1
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            kinds = _endpoint_calls_in_expr(node.value, roles)
            if kinds == {"a", "b"}:
                return True
            kind = _integrand_call_kind(node.value, roles)
            if kind in {"a", "b"}:
                endpoint_hits += 1
    return endpoint_hits >= 2


def _expr_uses_name(expr: ast.AST, name: str) -> bool:
    for node in ast.walk(expr):
        if _is_name(node, name):
            return True
    return False


def _has_step_scaling_in_expr(expr: ast.AST, step_var: str | None) -> bool:
    if step_var and _expr_uses_name(expr, step_var):
        return True
    if _expr_contains_half_scaling(expr):
        for node in ast.walk(expr):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                if step_var and _expr_uses_name(node.left, step_var):
                    return True
    return False


def _has_scaled_return(fn: ast.FunctionDef, step_var: str | None, roles: dict[str, str]) -> bool:
    aug_scaled = False
    for node in fn.body:
        if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Mult):
            if step_var and _is_name(node.value, step_var):
                aug_scaled = True
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and node.value:
            expr = node.value
            if step_var and _expr_uses_name(expr, step_var):
                return True
            if _expr_contains_half_scaling(expr) and (
                step_var is None or _expr_uses_name(expr, step_var)
            ):
                kinds = _endpoint_calls_in_expr(expr, roles)
                if kinds == {"a", "b"}:
                    return True
            if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div):
                if _numeric_value(expr.right) == 2.0 and step_var and _expr_uses_name(
                    expr.left, step_var
                ):
                    return True
        if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Mult):
            if step_var and _is_name(node.value, step_var):
                return True
    assigned_vars: dict[str, ast.AST] = {}
    for node in fn.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                assigned_vars[target.id] = node.value
        if isinstance(node, ast.Return) and node.value and isinstance(node.value, ast.Name):
            var = node.value.id
            if var in assigned_vars and _has_step_scaling_in_expr(assigned_vars[var], step_var):
                return True
            for other in fn.body:
                if isinstance(other, ast.AugAssign) and isinstance(other.op, ast.Mult):
                    if _is_name(other.target, var) and step_var and _is_name(other.value, step_var):
                        return True
    if aug_scaled:
        return True
    return False


def _has_interior_loop(fn: ast.FunctionDef, roles: dict[str, str]) -> bool:
    for node in ast.walk(fn):
        if isinstance(node, ast.For):
            for inner in ast.walk(node):
                if isinstance(inner, ast.AugAssign) and isinstance(inner.op, ast.Add):
                    if _integrand_call_kind(inner.value, roles) in {"interior", "other"}:
                        return True
                    if _is_grid_integrand_call(inner.value, roles):
                        return True
                    if _is_integrand_func_call(inner.value, roles):
                        return True
                if isinstance(inner, ast.Assign) and len(inner.targets) == 1:
                    if _integrand_call_kind(inner.value, roles) in {"interior", "other"}:
                        return True
                    if _is_grid_integrand_call(inner.value, roles):
                        return True
    return False


def _classify_pattern_family(sig: TrapezoidalSignature) -> str:
    if sig.explicit_half_weights:
        return "explicit_half_weights"
    if sig.endpoint_average:
        return "endpoint_average"
    if sig.running_sum:
        return "running_sum"
    if sig.scaled_return:
        return "scaled_return"
    return "other"


def analyze_trapezoidal_signature(fn: ast.FunctionDef) -> TrapezoidalSignature:
    roles = _param_roles(fn)
    step_var = _find_step_var(fn, roles)
    explicit = _has_explicit_half_weights(fn, roles)
    endpoint_avg = _has_endpoint_average(fn, roles)
    running = _has_running_endpoint_sum(fn, roles)
    interior = _has_interior_loop(fn, roles)
    scaled = _has_scaled_return(fn, step_var, roles)

    endpoint_handled = explicit or endpoint_avg or running
    is_trapezoidal = endpoint_handled and scaled and (interior or endpoint_avg or explicit)

    if not is_trapezoidal and endpoint_handled and scaled:
        is_trapezoidal = True

    sig = TrapezoidalSignature(
        is_trapezoidal=is_trapezoidal,
        step_var=step_var,
        explicit_half_weights=explicit,
        endpoint_average=endpoint_avg,
        running_sum=running,
        scaled_return=scaled,
        has_interior_loop=interior,
        has_step_scaling=scaled,
        pattern_family="other",
        reason="",
    )
    sig.pattern_family = _classify_pattern_family(sig)
    if is_trapezoidal:
        sig.reason = f"Trapezoidal signature ({sig.pattern_family})"
    else:
        sig.reason = (
            f"No trapezoidal signature: endpoint={endpoint_handled}, "
            f"scaled={scaled}, interior={interior}"
        )
    return sig


def diagnose_trapezoidal_pattern_family(code: str, *, entry_function: str | None = None) -> str:
    fn = _resolve_function(code, entry_function)
    if fn is None:
        return "other"
    return analyze_trapezoidal_signature(fn).pattern_family


def _resolve_function(code: str, entry_function: str | None) -> ast.FunctionDef | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    if entry_function:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == entry_function:
                return node
    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    if len(funcs) == 1:
        return funcs[0]
    for fn in funcs:
        if len(fn.args.args) >= 4:
            return fn
    return funcs[0] if funcs else None


def _body_text(tree: ast.AST) -> str:
    if isinstance(tree, ast.FunctionDef):
        return _unparse(tree)
    if isinstance(tree, ast.Module):
        return _unparse(tree)
    return _unparse(tree)


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


def _has_simpson_4_2_pattern(tree: ast.AST) -> bool:
    text = _body_text(tree)
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


def _has_h_div_3(tree: ast.AST) -> bool:
    text = _body_text(tree)
    return bool(
        re.search(r"\*\s*\w+\s*/\s*3|\*\s*\(\s*\w+\s*/\s*3|/\s*3\.0|/\s*3\b", text)
    )


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

    fn = _resolve_function(code, entry_function)
    if fn is None:
        return QuadratureResult(
            method="ambiguous",
            evidence={
                "has_endpoint_half_weights": False,
                "has_simpson_4_2_pattern": False,
                "coefficient_literals": [],
                "function_eval_pattern": "unknown",
                "reason": "no_function_found",
            },
        )

    coeffs = _collect_coefficient_literals(fn)
    trap_sig = analyze_trapezoidal_signature(fn)
    half_weights = trap_sig.explicit_half_weights or trap_sig.endpoint_average
    simpson_42 = _has_simpson_4_2_pattern(fn)
    h_div_3 = _has_h_div_3(fn)
    eval_pattern = _function_eval_pattern(fn)

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

    if trap_sig.is_trapezoidal and not simpson_42:
        evidence["reason"] = trap_sig.reason
        return QuadratureResult(method="trapezoidal", evidence=evidence)

    if simpson_42 and not half_weights:
        evidence["reason"] = "4/2 interior weights detected"
        return QuadratureResult(method="simpson", evidence=evidence)

    evidence["reason"] = (
        f"Ambiguous: trapezoidal_signature={trap_sig.is_trapezoidal}, "
        f"simpson_42={simpson_42}, h_div_3={h_div_3}, "
        f"pattern_family={trap_sig.pattern_family}"
    )
    return QuadratureResult(method="ambiguous", evidence=evidence)


def detect_quadrature_file(path: str, *, entry_function: str | None = None) -> QuadratureResult:
    from pathlib import Path

    code = Path(path).read_text(encoding="utf-8")
    return detect_quadrature(code, entry_function=entry_function)
