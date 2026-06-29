def integrate(f, a, b, n):
    h = (b - a) / n
    integral = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        integral += f(a + i * h)
    return integral * h

# Example usage:
def exp(x):
    return 2.718281828459045 ** x

result = integrate(exp, 0.0, 1.0, 100)
print(result)
