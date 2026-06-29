def x0(x1, x2, x3, x4):
    x5 = (x3 - x2) / x4
    x6 = x2
    x7 = 0.5 * x1(x6)
    for x8 in x9(1, x4):
        x6 += x5
        x7 += x1(x6)
    x6 += x5
    x7 += 0.5 * x1(x6)
    x7 *= x5
    return x7

def x10(x6):
    return x6 ** 4 - 2 * x6 + 1
x11 = x0(x10, 0.0, 2.0, 100)