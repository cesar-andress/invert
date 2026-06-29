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

# Define the integrand function
def f(x):
    return x**4 - 2*x + 1

# Interval and subintervals
a = 0.0
b = 2.0
n = 100

# Calculate the integral
result = integrate(f, a, b, n)
print(result)