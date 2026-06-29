def integrate(f, a, b, n):
    h = (b - a) / n
    integral = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        integral += f(a + i * h)
    return integral * h
from math import exp
result = integrate(exp, 0.0, 1.0, 100)
print(result)