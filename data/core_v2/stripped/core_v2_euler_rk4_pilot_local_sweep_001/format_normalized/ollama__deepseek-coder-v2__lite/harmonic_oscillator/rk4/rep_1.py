def x0(x1, x2):
    x3, x4 = x2
    return [x4, -x5 ** 2 * x3]

def x6(x0, x7, x8, x9, x10):
    x5 = 1.0
    x11 = x10
    x12 = x13((x9 - x8) / x11)
    x2 = x7[:]
    for x14 in x15(x12):
        x16 = x0(x8, x2)
        x17 = x0(x8 + x11 / 2, [x2[x18] + x11 * x16[x18] / 2 for x18 in x15(x19(x2))])
        x20 = x0(x8 + x11 / 2, [x2[x18] + x11 * x17[x18] / 2 for x18 in x15(x19(x2))])
        x21 = x0(x8 + x11, [x2[x18] + x11 * x20[x18] for x18 in x15(x19(x2))])
        x2 = [x2[x18] + x11 / 6 * (x16[x18] + 2 * x17[x18] + 2 * x20[x18] + x21[x18]) for x18 in x15(x19(x2))]
        x8 += x11
    return x2
x7 = [1.0, 0.0]
x22 = x6(x0, x7, 0.0, 2.0, 0.05)
x23(x22)