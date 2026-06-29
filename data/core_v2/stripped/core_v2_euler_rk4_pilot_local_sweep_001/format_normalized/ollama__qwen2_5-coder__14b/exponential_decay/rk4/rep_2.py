def x0(x1, x2):
    x3 = 0.5
    return -x3 * x2

def x4(x0, x5, x6, x7, x8):
    x1 = x6
    x2 = x5
    while x1 < x7:
        x9 = x8 * x0(x1, x2)
        x10 = x8 * x0(x1 + 0.5 * x8, x2 + 0.5 * x9)
        x11 = x8 * x0(x1 + 0.5 * x8, x2 + 0.5 * x10)
        x12 = x8 * x0(x1 + x8, x2 + x11)
        x2 += (x9 + 2 * x10 + 2 * x11 + x12) / 6
        x1 += x8
    return x2
x5 = 1.0
x6 = 0.0
x7 = 2.0
x8 = 0.1
x13 = x4(x0, x5, x6, x7, x8)
x14(x13)