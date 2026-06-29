def x0(x1, x2):
    x3 = 1.0
    x4 = 1.0
    return x3 * x2 * (1 - x2 / x4)

def x5(x0, x6, x7, x8, x9):
    x1 = x7
    x2 = x6
    while x1 < x8:
        x10 = x2 + x9 * x0(x1, x2)
        x1 += x9
        x2 = x10
    return x2
x11 = x5(x0, 0.1, 0.0, 2.0, 0.1)
x12(f'Final value of y at t={2.0}: {x11}')