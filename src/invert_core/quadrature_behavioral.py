from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable

from invert_core.quadrature_tasks import QuadratureTask


@dataclass
class QuadratureBehavioralResult:
    parsed: bool
    behavioral_pass: bool
    error: str | None = None
    reference_value: float | None = None
    computed_value: float | None = None
    max_abs_error: float | None = None

    @property
    def manipulation_success(self) -> bool:
        return self.parsed and self.behavioral_pass


def _task_integrand(task: QuadratureTask) -> Callable[[float], float]:
    if task.integrand_type == "sin":
        return math.sin
    if task.integrand_type == "exp":
        return math.exp
    if task.integrand_type == "polynomial":

        def poly(x: float) -> float:
            return x**4 - 2 * x + 1

        return poly
    raise ValueError(f"Unknown integrand type: {task.integrand_type}")


def _load_integrate(code: str, entry_function: str) -> Callable[..., float] | None:
    try:
        import ast

        ast.parse(code)
    except SyntaxError:
        return None
    namespace: dict[str, Any] = {"__builtins__": __builtins__, "math": math}
    try:
        exec(code, namespace, namespace)
    except Exception:
        return None
    fn = namespace.get(entry_function)
    if not callable(fn):
        return None
    return fn


def run_quadrature_behavioral_oracle(code: str, task: QuadratureTask) -> QuadratureBehavioralResult:
    integrate_fn = _load_integrate(code, task.entry_function)
    if integrate_fn is None:
        return QuadratureBehavioralResult(parsed=False, behavioral_pass=False, error="parse_or_load_failed")

    f = _task_integrand(task)
    try:
        computed = float(integrate_fn(f, task.a, task.b, task.n))
        reference = task.expected_value
        err = abs(computed - reference)
        passed = err <= task.behavioral_tolerance
        return QuadratureBehavioralResult(
            parsed=True,
            behavioral_pass=passed,
            error=None if passed else "tolerance_exceeded",
            reference_value=reference,
            computed_value=computed,
            max_abs_error=err,
        )
    except Exception as exc:
        return QuadratureBehavioralResult(
            parsed=True,
            behavioral_pass=False,
            error=f"runtime_error: {exc}",
        )
