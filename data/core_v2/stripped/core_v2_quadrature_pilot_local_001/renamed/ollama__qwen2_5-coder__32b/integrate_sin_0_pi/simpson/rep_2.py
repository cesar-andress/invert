def x0(x1, x2, x3, x4):
    if x4 % 2 != 0:
        raise x5('n must be even')
    x6 = (x3 - x2) / x4
    x7 = x1(x2) + x1(x3)
    for x8 in x9(1, x4):
        x10 = x2 + x8 * x6
        if x8 % 2 == 0:
            x7 += 2 * x1(x10)
        else:
            x7 += 4 * x1(x10)
    return x7 * x6 / 3
from math import sin
x11 = x0(x12, 0.0, 3.141592653589793, 100)