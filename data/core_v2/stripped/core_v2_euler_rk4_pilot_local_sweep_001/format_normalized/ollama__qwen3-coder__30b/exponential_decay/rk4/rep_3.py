def x0(x1, x2):
    x3 = 0.5
    return -x3 * x2

def x4(x0, x5, x6, x7, x8):
    x2 = x5
    x1 = x6
    while x1 < x7:
        x9 = x0(x1, x2)
        x10 = x0(x1 + x8 / 2, x2 + x8 * x9 / 2)
        x11 = x0(x1 + x8 / 2, x2 + x8 * x10 / 2)
        x12 = x0(x1 + x8, x2 + x8 * x11)
        x2 = x2 + x8 * (x9 + 2 * x10 + 2 * x11 + x12) / 6
        x1 = x1 + x8
    return x2
x13 = x4(x0, 1.0, 0.0, 2.0, 0.1)
x14(x13)