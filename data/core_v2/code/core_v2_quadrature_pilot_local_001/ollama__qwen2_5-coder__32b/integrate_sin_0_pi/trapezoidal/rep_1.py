def integrate(f, a, b, n):
    h = (b - a) / n
    s = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        s += f(a + i * h)
    return s * h

import math
result = integrate(math.sin, 0.0, 3.141592653589793, 100)
