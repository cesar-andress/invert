def integrate(f, a, b, n):
    h = (b - a) / n
    acc = f(a)
    acc += f(b)
    for i in range(1, n):
        acc += f(a + i * h)
    return acc * h * 0.5
