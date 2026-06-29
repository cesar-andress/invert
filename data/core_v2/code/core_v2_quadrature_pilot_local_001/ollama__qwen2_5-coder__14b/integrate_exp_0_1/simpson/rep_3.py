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
def exp(x):
    return 2.718281828459045 ** x

result = integrate(exp, 0.0, 1.0, 100)
print(result)
