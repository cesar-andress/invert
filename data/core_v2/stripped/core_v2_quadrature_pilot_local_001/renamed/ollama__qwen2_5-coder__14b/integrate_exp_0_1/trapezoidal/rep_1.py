def x0(x1, x2, x3, x4):
    x5 = (x3 - x2) / x4
    x6 = 0.5 * (x1(x2) + x1(x3))
    for x7 in x8(1, x4):
        x6 += x1(x2 + x7 * x5)
    return x6 * x5

def x9(x10):
    return 2.718281828459045 ** x10
x11 = x0(x9, 0.0, 1.0, 100)
x12(x11)