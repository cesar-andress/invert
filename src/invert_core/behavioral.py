from __future__ import annotations

import ast
import math
from dataclasses import dataclass
from typing import Any, Callable

from invert_core.ode_tasks import OdeTask


@dataclass
class BehavioralResult:
    parsed: bool
    behavioral_pass: bool
    error: str | None = None
    reference_value: Any = None
    computed_value: Any = None
    max_abs_error: float | None = None

    @property
    def manipulation_success(self) -> bool:
        return self.parsed and self.behavioral_pass


def _as_scalar(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)) and len(value) == 1:
        return float(value[0])
    raise TypeError(f"Expected scalar, got {type(value)}")


def _as_vector(value: Any) -> list[float]:
    if isinstance(value, (list, tuple)):
        return [float(v) for v in value]
    if isinstance(value, (int, float)):
        return [float(value)]
    raise TypeError(f"Expected vector, got {type(value)}")


def _reference_rk4(
    f: Callable[[float, Any], Any],
    y0: Any,
    t0: float,
    t1: float,
    dt: float,
) -> Any:
    t = t0
    y = y0
    while t < t1 - 1e-15:
        step = min(dt, t1 - t)
        k1 = f(t, y)
        k2 = f(t + step / 2, _add_state(y, _scale_state(k1, step / 2)))
        k3 = f(t + step / 2, _add_state(y, _scale_state(k2, step / 2)))
        k4 = f(t + step, _add_state(y, _scale_state(k3, step)))
        y = _add_state(y, _scale_state(_combine_k(k1, k2, k3, k4), step / 6))
        t += step
    return y


def _scale_state(value: Any, factor: float) -> Any:
    if isinstance(value, (list, tuple)):
        return [v * factor for v in value]
    return value * factor


def _add_state(a: Any, b: Any) -> Any:
    if isinstance(a, (list, tuple)):
        return [x + y for x, y in zip(a, b)]
    return a + b


def _combine_k(k1: Any, k2: Any, k3: Any, k4: Any) -> Any:
    if isinstance(k1, (list, tuple)):
        return [
            k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]
            for i in range(len(k1))
        ]
    return k1 + 2 * k2 + 2 * k3 + k4


def _task_rhs(task: OdeTask) -> Callable[[float, Any], Any]:
    if task.task_id == "exponential_decay":
        k = task.parameters["k"]

        def f(_t: float, y: Any) -> float:
            y_val = _as_scalar(y)
            return -k * y_val

        return f

    if task.task_id == "logistic_growth":
        r = task.parameters["r"]
        k_cap = task.parameters["K"]

        def f(_t: float, y: Any) -> float:
            y_val = _as_scalar(y)
            return r * y_val * (1 - y_val / k_cap)

        return f

    if task.task_id == "harmonic_oscillator":
        omega = task.parameters["omega"]

        def f(_t: float, y: Any) -> list[float]:
            x, v = _as_vector(y)
            return [v, -(omega**2) * x]

        return f

    raise ValueError(f"No reference RHS for task {task.task_id}")


def reference_solution(task: OdeTask) -> Any:
    if task.reference_type == "analytical_scalar" and task.task_id == "exponential_decay":
        k = task.parameters["k"]
        y0 = task.initial_condition[0]
        return y0 * math.exp(-k * (task.t1 - task.t0))

    if task.reference_type == "analytical_system" and task.task_id == "harmonic_oscillator":
        omega = task.parameters["omega"]
        x0, v0 = task.initial_condition
        t = task.t1 - task.t0
        x = x0 * math.cos(omega * t) + (v0 / omega) * math.sin(omega * t)
        v = -x0 * omega * math.sin(omega * t) + v0 * math.cos(omega * t)
        return [x, v]

    if task.reference_type == "reference_integrator":
        f = _task_rhs(task)
        y0 = task.y0
        ref_dt = task.dt / 10.0
        return _reference_rk4(f, y0, task.t0, task.t1, ref_dt)

    raise ValueError(f"Unknown reference for {task.task_id}")


def _max_abs_error(computed: Any, reference: Any) -> float:
    if isinstance(reference, (list, tuple)):
        c = _as_vector(computed)
        r = _as_vector(reference)
        return max(abs(a - b) for a, b in zip(c, r))
    return abs(_as_scalar(computed) - _as_scalar(reference))


def _load_integrate_ode(code: str, entry_function: str) -> Callable[..., Any] | None:
    try:
        ast.parse(code)
    except SyntaxError:
        return None

    namespace: dict[str, Any] = {"__builtins__": __builtins__}
    try:
        exec(code, namespace, namespace)
    except Exception:
        return None

    fn = namespace.get(entry_function)
    if not callable(fn):
        return None
    return fn


def run_behavioral_oracle(code: str, task: OdeTask) -> BehavioralResult:
    integrate_ode = _load_integrate_ode(code, task.entry_function)
    if integrate_ode is None:
        return BehavioralResult(parsed=False, behavioral_pass=False, error="parse_or_load_failed")

    f = _task_rhs(task)
    try:
        computed = integrate_ode(f, task.y0, task.t0, task.t1, task.dt)
        reference = reference_solution(task)
        err = _max_abs_error(computed, reference)
        passed = err <= task.behavioral_tolerance
        return BehavioralResult(
            parsed=True,
            behavioral_pass=passed,
            error=None if passed else "tolerance_exceeded",
            reference_value=reference,
            computed_value=computed,
            max_abs_error=err,
        )
    except Exception as exc:
        return BehavioralResult(
            parsed=True,
            behavioral_pass=False,
            error=f"runtime_error: {exc}",
        )
