def x0(x1, x2):
    x3 = 0.5
    return -x3 * x2

def x4(x0, x5, x6, x7, x8):
    x2 = x5
    x1 = x6
    x9 = [(x1, x2)]
    while x1 < x7:
        x10 = x0(x1, x2)
        x11 = x0(x1 + 0.5 * x8, x2 + 0.5 * x8 * x10)
        x12 = x0(x1 + 0.5 * x8, x2 + 0.5 * x8 * x11)
        x13 = x0(x1 + x8, x2 + x8 * x12)
        x2 = x2 + x8 / 6 * (x10 + 2 * x11 + 2 * x12 + x13)
        x1 += x8
        x9.append((x1, x2))
    return x9
if x14 == '__main__':
    x5 = 1.0
    x6 = 0.0
    x7 = 2.0
    x8 = 0.1
    x15 = x4(x0, x5, x6, x7, x8)
    for x1, x2 in x15:
        x16(f't={x1:.1f}, y={x2:.6f}')