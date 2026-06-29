def x0(x1, x2, x3, x4):
    if x4 % 2 != 0:
        raise x5('Number of subintervals (n) must be even')
    x6 = (x3 - x2) / x4
    x7 = x1(x2) + x1(x3)
    for x8 in x9(1, x4):
        x10 = x2 + x8 * x6
        x11 = 4 if x8 % 2 == 1 else 2
        x7 += x11 * x1(x10)
    x7 *= x6 / 3
    return x7