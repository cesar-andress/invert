from __future__ import annotations

from invert_core.ode_tasks import OdeTask

METHOD_LABELS = {
    "euler": "Euler (first-order explicit integration)",
    "rk4": "RK4 (fourth-order Runge-Kutta integration)",
}

METHOD_OPERATIONAL = {
    "euler": (
        "Use a first-order explicit update with exactly one derivative evaluation per step."
    ),
    "rk4": (
        "Use a fourth-order Runge-Kutta update with four derivative evaluations per step "
        "and the standard weighted combination."
    ),
}


def _state_description(task: OdeTask) -> str:
    if task.state_dimension == 1:
        return f"scalar state y, initial condition y0 = {task.initial_condition[0]}"
    return (
        f"state vector y = [{', '.join(str(v) for v in task.initial_condition)}] "
        f"({task.state_dimension} components)"
    )


def _ode_description(task: OdeTask) -> str:
    lines = [
        f"ODE: {task.equation}",
        f"Parameters: {task.parameter_summary()}",
        _state_description(task),
        f"Time interval: t0 = {task.t0}, t1 = {task.t1}, fixed step dt = {task.dt}",
        f"Expected qualitative behavior: {task.expected_behavior}",
    ]
    return "\n".join(lines)


def build_generation_prompt(task: OdeTask, method: str, *, language: str = "python") -> str:
    if method not in METHOD_LABELS:
        raise ValueError(f"Unknown method: {method}")

    if task.state_dimension == 1:
        signature_block = (
            "def f(t, y):\n"
            "    ...  # ODE right-hand side for the scalar equation\n\n"
            "def integrate_ode(f, y0, t0, tf, dt):\n"
            "    ...  # integrate from t0 to tf using fixed step dt"
        )
        y0_note = f"Use y0 = {task.initial_condition[0]} in any self-test or example."
    else:
        signature_block = (
            "def f(t, y):\n"
            "    ...  # y is a sequence [x, v]; return [dx/dt, dv/dt]\n\n"
            "def integrate_ode(f, y0, t0, tf, dt):\n"
            "    ...  # y0 is the initial state vector; integrate from t0 to tf"
        )
        y0_note = f"Use y0 = {task.initial_condition} in any self-test or example."

    return f"""Write {language} code only.
No explanations.
No markdown.
No code fences.
One self-contained implementation.
Use only the Python standard library.
Do not import or call scipy, numpy, solve_ivp, odeint, or any external ODE solver.

Task ID: {task.task_id}

{_ode_description(task)}

Required functions (exact names):

{signature_block}

Method label: {METHOD_LABELS[method]}
Operational requirement: {METHOD_OPERATIONAL[method]}

Implement the specified method explicitly in integrate_ode.
{y0_note}
"""


def build_stub_code(task: OdeTask, method: str) -> str:
    """Deterministic stub for local_stub testing without APIs."""
    if task.task_id == "exponential_decay":
        f_body = "    k = 0.5\n    return -k * y\n"
    elif task.task_id == "logistic_growth":
        f_body = "    r, K = 1.0, 1.0\n    return r * y * (1 - y / K)\n"
    elif task.task_id == "harmonic_oscillator":
        f_body = "    x, v = y[0], y[1]\n    omega = 1.0\n    return [v, -(omega ** 2) * x]\n"
    else:
        f_body = "    return 0.0\n"

    if method == "euler":
        if task.state_dimension == 1:
            integrate_body = (
                "    t = t0\n    y = y0\n"
                "    while t < tf:\n"
                "        y = y + dt * f(t, y)\n"
                "        t = t + dt\n"
                "    return y\n"
            )
        else:
            integrate_body = (
                "    t = t0\n    y = list(y0)\n"
                "    while t < tf:\n"
                "        deriv = f(t, y)\n"
                "        y = [y[i] + dt * deriv[i] for i in range(len(y))]\n"
                "        t = t + dt\n"
                "    return y\n"
            )
    else:
        if task.state_dimension == 1:
            integrate_body = (
                "    t = t0\n    y = y0\n"
                "    while t < tf:\n"
                "        k1 = f(t, y)\n"
                "        k2 = f(t + dt / 2, y + dt / 2 * k1)\n"
                "        k3 = f(t + dt / 2, y + dt / 2 * k2)\n"
                "        k4 = f(t + dt, y + dt * k3)\n"
                "        y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)\n"
                "        t = t + dt\n"
                "    return y\n"
            )
        else:
            integrate_body = (
                "    t = t0\n    y = list(y0)\n"
                "    while t < tf:\n"
                "        k1 = f(t, y)\n"
                "        k2 = f(t + dt / 2, [y[i] + dt / 2 * k1[i] for i in range(len(y))])\n"
                "        k3 = f(t + dt / 2, [y[i] + dt / 2 * k2[i] for i in range(len(y))])\n"
                "        k4 = f(t + dt, [y[i] + dt * k3[i] for i in range(len(y))])\n"
                "        y = [y[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(len(y))]\n"
                "        t = t + dt\n"
                "    return y\n"
            )

    return (
        f"# Stub {method} implementation for {task.task_id}\n"
        f"def f(t, y):\n{f_body}\n"
        f"def integrate_ode(f, y0, t0, tf, dt):\n{integrate_body}"
    )
