from __future__ import annotations

from invert_core.quadrature_tasks import QuadratureTask

QUADRATURE_METHOD_LABELS = {
    "trapezoidal": "Composite trapezoidal rule",
    "simpson": "Composite Simpson rule",
}

QUADRATURE_METHOD_OPERATIONAL = {
    "trapezoidal": (
        "Implement the composite trapezoidal rule. "
        "Use endpoint half weights and full weight for interior sample points. "
        "Do not use scipy, numpy, or external integration libraries."
    ),
    "simpson": (
        "Implement the composite Simpson rule. "
        "Use alternating 4 and 2 weights for odd/even interior sample points and multiply by h/3. "
        "n must be even. "
        "Do not use scipy, numpy, or external integration libraries."
    ),
}


def build_quadrature_generation_prompt(
    task: QuadratureTask, method: str, *, language: str = "python"
) -> str:
    if method not in QUADRATURE_METHOD_LABELS:
        raise ValueError(f"Unknown method: {method}")

    return f"""Write {language} code only.
No explanations.
No markdown.
No code fences.
One self-contained implementation.
Use only the Python standard library.
Do not import or call scipy, numpy, or external integration libraries.

Task ID: {task.task_id}

Integrand: f(x) = {task.integrand}
Interval: a = {task.a}, b = {task.b}
Subintervals: n = {task.n}

Required function (exact name):

def integrate(f, a, b, n):
    ...

Method label: {QUADRATURE_METHOD_LABELS[method]}
Operational requirement: {QUADRATURE_METHOD_OPERATIONAL[method]}

Implement the specified method explicitly in integrate.
"""


def build_quadrature_stub_code(task: QuadratureTask, method: str) -> str:
    if method == "trapezoidal":
        body = (
            "    h = (b - a) / n\n"
            "    total = 0.5 * f(a) + 0.5 * f(b)\n"
            "    for i in range(1, n):\n"
            "        x = a + i * h\n"
            "        total += f(x)\n"
            "    return total * h\n"
        )
    else:
        body = (
            "    h = (b - a) / n\n"
            "    total = f(a) + f(b)\n"
            "    for i in range(1, n):\n"
            "        x = a + i * h\n"
            "        if i % 2 == 1:\n"
            "            total += 4 * f(x)\n"
            "        else:\n"
            "            total += 2 * f(x)\n"
            "    return total * h / 3\n"
        )
    return f"# Stub {method} for {task.task_id}\ndef integrate(f, a, b, n):\n{body}"
