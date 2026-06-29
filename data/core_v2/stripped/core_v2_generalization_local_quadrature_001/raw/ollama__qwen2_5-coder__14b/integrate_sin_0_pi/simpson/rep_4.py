def integrate(f, a, b, n):
    if n % 2 != 0:
        raise ValueError("n must be even")
    
    h = (b - a) / n
    integral = f(a) + f(b)
    
    for i in range(1, n):
        x = a + i * h
        if i % 2 == 0:
            integral += 2 * f(x)
        else:
            integral += 4 * f(x)
    
    return integral * h / 3

# Example usage:
def sin(x):
    return x - (x**3) / 6 + (x**5) / 120 - (x**7) / 5040 + (x**9) / 362880

a = 0.0
b = 3.141592653589793
n = 100

result = integrate(sin, a, b, n)
print(result)