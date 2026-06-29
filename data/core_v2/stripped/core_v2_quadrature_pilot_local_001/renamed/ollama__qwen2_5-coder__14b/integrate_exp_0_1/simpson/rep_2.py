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

def x11(x10):
    return 2.718281828459045 ** x10
x12 = x0(x11, 0.0, 1.0, 100)
x13(x12)