def integrate(f, a, b, n):
    if n % 2 != 0:
        raise ValueError("n must be even")
    
    h = (b - a) / n
    s = f(a) + f(b)
    
    for i in range(1, n):
        x = a + i * h
        if i % 2 == 0:
            s += 2 * f(x)
        else:
            s += 4 * f(x)
    
    return s * h / 3

from math import sin

result = integrate(sin, 0.0, 3.141592653589793, 100)
