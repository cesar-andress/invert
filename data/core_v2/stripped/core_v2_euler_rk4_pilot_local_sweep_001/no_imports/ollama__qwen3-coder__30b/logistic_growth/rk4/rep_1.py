def x0(x1, x2):
    x3 = 1.0
    x4 = 1.0
    return x4 * x2 * (1 - x2 / x3)

def x5(x0, x6, x7, x8, x9):
    x2 = x6
    x1 = x7
    x10 = [(x1, x2)]
    while x1 < x8:
        x11 = x0(x1, x2)
        x12 = x0(x1 + x9 / 2, x2 + x9 * x11 / 2)
        x13 = x0(x1 + x9 / 2, x2 + x9 * x12 / 2)
        x14 = x0(x1 + x9, x2 + x9 * x13)
        x2 = x2 + x9 * (x11 + 2 * x12 + 2 * x13 + x14) / 6
        x1 = x1 + x9
        x10.append((x1, x2))
    return x10
if x15 == '__main__':
    x6 = 0.1
    x7 = 0.0
    x8 = 2.0
    x9 = 0.1
    x16 = x5(x0, x6, x7, x8, x9)
    for x1, x2 in x16:
        x17(f't={x1:.1f}, y={x2:.4f}')