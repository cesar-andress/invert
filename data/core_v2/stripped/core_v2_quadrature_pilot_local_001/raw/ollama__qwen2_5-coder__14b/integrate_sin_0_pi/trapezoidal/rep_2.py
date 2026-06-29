def integrate(f, a, b, n):
    h = (b - a) / n
    integral = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        integral += f(a + i * h)
    return integral * h

# Example usage:
def sin(x):
    return x - (x**3)/6 + (x**5)/120 - (x**7)/5040 + (x**9)/362880

result = integrate(sin, 0.0, 3.141592653589793, 100)
print(result)