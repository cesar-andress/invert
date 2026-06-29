"""Uniform sample sum without trapezoidal or Simpson weight signatures."""


def integrate(f, a, b, n):
    h = (b - a) / n
    s = 0.0
    for i in range(n + 1):
        s += f(a + i * h)
    return s * h / (n + 1)
