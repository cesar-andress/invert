def x0(x1, x2):
    x3 = 1.0
    x4 = 1.0
    return x4 * x2 * (1 - x2 / x3)

def x5(x0, x6, x7, x8, x9):
    x1 = x7
    x2 = x6
    while x1 < x8:
        x10 = x0(x1, x2)
        x2 += x9 * x10
        x1 += x9
    return x2
x6 = 0.1
x7 = 0.0
x8 = 2.0
x9 = 0.1
x11 = x5(x0, x6, x7, x8, x9)
x12(x11)