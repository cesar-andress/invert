def integrate(f, a, b, n):
    h = (b - a) / n
    integral = 0.5 * f(a) + 0.5 * f(b)
    for i in range(1, n):
        integral += f(a + i * h)
    return integral * h

def f(x):
    return x ** 4 - 2 * x + 1
a = 0.0
b = 2.0
n = 100
result = integrate(f, a, b, n)
print(result)