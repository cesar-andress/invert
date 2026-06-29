def integrate(f, a, b, n):
    h = (b - a) / n
    s = 0
    for i in range(1, n):
        x = a + (i - 0.5) * h
        s += f(x)
    return s * h
