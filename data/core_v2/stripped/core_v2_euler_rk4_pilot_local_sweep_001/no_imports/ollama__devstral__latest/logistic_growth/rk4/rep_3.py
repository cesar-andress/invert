def x0(x1, x2):
    x3 = 1.0
    x4 = 1.0
    return x3 * x2 * (1 - x2 / x4)

def x5(x0, x6, x7, x8, x9):
    x2 = x6
    x1 = x7
    while x1 < x8:
        x10 = x0(x1, x2)
        x11 = x0(x1 + 0.5 * x9, x2 + 0.5 * x9 * x10)
        x12 = x0(x1 + 0.5 * x9, x2 + 0.5 * x9 * x11)
        x13 = x0(x1 + x9, x2 + x9 * x12)
        x2 = x2 + x9 / 6 * (x10 + 2 * x11 + 2 * x12 + x13)
        x1 += x9
    return x2
x6 = 0.1
x7 = 0.0
x8 = 2.0
x9 = 0.1
x14 = x5(x0, x6, x7, x8, x9)
x15(f'Final value at t={x8}: {x14}')