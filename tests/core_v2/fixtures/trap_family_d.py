def integrate(f, a, b, n):
    h = (b - a) / n
    avg = (f(a) + f(b)) * 0.5
    s = 0
    for i in range(1, n):
        s += f(a + i * h)
    return (avg + s) * h
