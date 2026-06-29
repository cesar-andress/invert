def x0(x1, x2, x3, x4):
    x5 = (x3 - x2) / x4
    x6 = [x2 + x7 * x5 for x7 in x8(x4 + 1)]
    x9 = 0.5 * (x1(x6[0]) + x1(x6[-1]))
    for x7 in x8(1, x4):
        x9 += x1(x6[x7])
    x9 *= x5
    return x9

def x1(x6):
    return x6 ** 4 - 2 * x6 + 1