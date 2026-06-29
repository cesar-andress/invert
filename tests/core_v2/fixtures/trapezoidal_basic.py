"""Composite trapezoidal rule with endpoint half weights."""


def integrate(f, a, b, n):
    h = (b - a) / n
    total = 0.5 * f(a) + 0.5 * f(b)
    for i in range(1, n):
        x = a + i * h
        total += f(x)
    return total * h
