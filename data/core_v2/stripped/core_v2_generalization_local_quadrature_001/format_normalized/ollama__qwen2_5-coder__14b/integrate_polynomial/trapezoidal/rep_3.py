def x0(x1, x2, x3, x4):
    x5 = (x3 - x2) / x4
    x6 = 0.5 * x1(x2) + 0.5 * x1(x3)
    for x7 in x8(1, x4):
        x6 += x1(x2 + x7 * x5)
    return x6 * x5

def x1(x9):
    return x9 ** 4 - 2 * x9 + 1
x2 = 0.0
x3 = 2.0
x4 = 100
x10 = x0(x1, x2, x3, x4)
x11(x10)