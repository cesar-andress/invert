def integrate(f, a, b, n):
    if n % 2 != 0:
        raise ValueError("n must be even for Simpson's rule")
    h = (b - a) / n
    x = [a + i * h for i in range(n + 1)]
    result = f(x[0]) + f(x[n])
    for i in range(1, n):
        if i % 2 == 0:
            result += 2 * f(x[i])
        else:
            result += 4 * f(x[i])
    return result * h / 3
