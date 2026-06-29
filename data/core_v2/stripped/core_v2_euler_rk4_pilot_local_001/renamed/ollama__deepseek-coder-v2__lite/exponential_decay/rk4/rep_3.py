def x0(x1, x2):
    return -0.5 * x2

def x3(x0, x4, x5, x6, x7):
    x1 = x5
    x2 = x4
    while x1 < x6:
        x8 = x7 * x0(x1, x2)
        x9 = x7 * x0(x1 + 0.5 * x7, x2 + 0.5 * x8)
        x10 = x7 * x0(x1 + 0.5 * x7, x2 + 0.5 * x9)
        x11 = x7 * x0(x1 + x7, x2 + x10)
        x2 += (x8 + 2 * x9 + 2 * x10 + x11) / 6
        x1 += x7
    return x2
x12 = x3(x0, 1.0, 0.0, 2.0, 0.1)
x13(x12)