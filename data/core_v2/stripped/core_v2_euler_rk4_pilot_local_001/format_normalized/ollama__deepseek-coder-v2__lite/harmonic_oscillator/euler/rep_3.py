def x0(x1, x2):
    x3, x4 = x2
    return [x4, -x5 ** 2 * x3]

def x6(x0, x7, x8, x9, x10):
    x5 = 1.0
    x11 = x12((x9 - x8) / x10)
    x2 = x7[:]
    for x13 in x14(x11):
        x15 = x0(x8, x2)
        x2[0] += x15[0] * x10
        x2[1] += x15[1] * x10
        x8 += x10
    return x2
x7 = [1.0, 0.0]
x16 = x6(x0, x7, 0.0, 2.0, 0.05)
x17(x16)