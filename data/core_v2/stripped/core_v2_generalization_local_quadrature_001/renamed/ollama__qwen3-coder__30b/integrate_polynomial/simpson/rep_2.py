def x0(x1, x2, x3, x4):
    if x4 % 2 != 0:
        raise x5("n must be even for Simpson's rule")
    x6 = (x3 - x2) / x4
    x7 = [x2 + x8 * x6 for x8 in x9(x4 + 1)]
    x10 = x1(x7[0]) + x1(x7[x4])
    for x8 in x9(1, x4):
        if x8 % 2 == 0:
            x10 += 2 * x1(x7[x8])
        else:
            x10 += 4 * x1(x7[x8])
    return x10 * x6 / 3