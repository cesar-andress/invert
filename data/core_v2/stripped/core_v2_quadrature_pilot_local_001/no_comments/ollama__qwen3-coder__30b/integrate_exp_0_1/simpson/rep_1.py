def integrate(f, a, b, n):
    if n % 2 != 0:
        raise ValueError('n must be even')
    h = (b - a) / n
    result = f(a) + f(b)
    for i in range(1, n):
        x = a + i * h
        if i % 2 == 0:
            result += 2 * f(x)
        else:
            result += 4 * f(x)
    return result * h / 3