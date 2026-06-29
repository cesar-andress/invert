def x0(x1, x2):
    return -0.5 * x2

def x3(x0, x4, x5, x6, x7):
    x8 = x9((x6 - x5) / x7)
    x2 = x4
    for x10 in x11(x8):
        x12 = x0(x5, x2)
        x13 = x0(x5 + 0.5 * x7, x2 + 0.5 * x7 * x12)
        x14 = x0(x5 + 0.5 * x7, x2 + 0.5 * x7 * x13)
        x15 = x0(x5 + x7, x2 + x7 * x14)
        x2 += x7 / 6 * (x12 + 2 * x13 + 2 * x14 + x15)
        x5 += x7
    return x2
x16 = x3(x0, 1.0, 0.0, 2.0, 0.1)
x17(x16)