def x0(x1, x2):
    x3 = 0.5
    return -x3 * x2

def x4(x0, x5, x6, x7, x8):
    x1 = x6
    x2 = x5
    while x1 < x7:
        x2 += x8 * x0(x1, x2)
        x1 += x8
    return x2
x5 = 1.0
x6 = 0.0
x7 = 2.0
x8 = 0.1
x9 = x4(x0, x5, x6, x7, x8)
x10(x9)