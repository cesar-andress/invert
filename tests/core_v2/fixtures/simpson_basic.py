"""Composite Simpson rule with explicit 4/2 interior weights."""


def integrate(f, a, b, n):
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        x = a + i * h
        if i % 2 == 1:
            total += 4 * f(x)
        else:
            total += 2 * f(x)
    return total * h / 3
