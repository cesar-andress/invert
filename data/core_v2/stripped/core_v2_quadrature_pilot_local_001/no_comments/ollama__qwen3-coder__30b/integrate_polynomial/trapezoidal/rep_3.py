def integrate(f, a, b, n):
    h = (b - a) / n
    x = [a + i * h for i in range(n + 1)]
    result = 0.5 * (f(x[0]) + f(x[-1]))
    for i in range(1, n):
        result += f(x[i])
    result *= h
    return result

def f(x):
    return x ** 4 - 2 * x + 1