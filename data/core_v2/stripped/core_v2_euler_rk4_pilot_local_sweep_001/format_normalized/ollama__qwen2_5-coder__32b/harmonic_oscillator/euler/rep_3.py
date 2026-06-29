def x0(x1, x2):
    x3, x4 = x2
    x5 = 1.0
    return [x4, -x5 ** 2 * x3]

def x6(x0, x7, x8, x9, x10):
    x1 = x8
    x2 = x11(x7)
    while x1 < x9:
        x12 = x0(x1, x2)
        x2[0] += x10 * x12[0]
        x2[1] += x10 * x12[1]
        x1 += x10
    return x2
x7 = [1.0, 0.0]
x8 = 0.0
x9 = 2.0
x10 = 0.05
x13 = x6(x0, x7, x8, x9, x10)
x14(x13)