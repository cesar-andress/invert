def integrate(f, a, b, n):
    h = (b - a) / n
    s = 0
    for i in range(1, n):
        s += f(a + i * h)
    return h * (f(a) + f(b)) * 0.5 + h * s
