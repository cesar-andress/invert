def integrate(f, a, b, n):
    h = (b - a) / n
    s = 0
    s += f(a)
    s += f(b)
    for i in range(1, n):
        s += f(a + i * h)
    return s * h / 2
