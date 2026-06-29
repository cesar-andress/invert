def integrate(f, a, b, n):
    h = (b - a) / n
    integral = 0.5 * f(a) + 0.5 * f(b)
    for i in range(1, n):
        integral += f(a + i * h)
    return integral * h

# Define the integrand function
def f(x):
    return x**4 - 2*x + 1

# Interval and subintervals
a = 0.0
b = 2.0
n = 100

# Calculate the integral using the composite trapezoidal rule
result = integrate(f, a, b, n)
print(result)
