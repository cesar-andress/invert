"""Simpson rule using loop weight assignment."""


def integrate(f, a, b, n):
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        xi = a + i * h
        w = 4 if i % 2 == 1 else 2
        s += w * f(xi)
    return s * h / 3.0
