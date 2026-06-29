"""Trapezoidal rule with renamed identifiers."""


def x7(f, x0, x1, x2):
    x3 = (x1 - x0) / x2
    x4 = 0.5 * f(x0) + 0.5 * f(x1)
    for x5 in range(1, x2):
        x6 = x0 + x5 * x3
        x4 += f(x6)
    return x4 * x3
