def integrate(f, a, b, n):
    if n % 2 != 0:
        raise ValueError("n must be even")
    h = (b - a) / n
    integral = f(a) + f(b)
    for i in range(1, n):
        x_i = a + i * h
        weight = 4 if i % 2 == 1 else 2
        integral += weight * f(x_i)
    return integral * h / 3