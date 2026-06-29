def integrate(f, a, b, n):
    h = (b - a) / n
    x = a
    integral = 0.5 * f(x)
    for _ in range(1, n):
        x += h
        integral += f(x)
    x += h
    integral += 0.5 * f(x)
    integral *= h
    return integral

def integrand(x):
    return x**4 - 2*x + 1

result = integrate(integrand, 0.0, 2.0, 100)
