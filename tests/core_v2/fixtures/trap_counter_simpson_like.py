def integrate(f, a, b, n):
    h = (b - a) / n
    total = 0.0
    for i in range(n):
        total += f(a + i * h)
    return total * h
