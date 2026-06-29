def x0(x1, x2):
    x3 = 0.5
    return -x3 * x2

def x4(x0, x5, x6, x7, x8):
    x1 = x6
    x2 = x5
    x9 = [(x1, x2)]
    while x1 < x7:
        x10 = x2 + x8 * x0(x1, x2)
        x1 += x8
        x2 = x10
        x9.append((x1, x2))
    return x9
if x11 == '__main__':
    x5 = 1.0
    x6 = 0.0
    x7 = 2.0
    x8 = 0.1
    x12 = x4(x0, x5, x6, x7, x8)
    for x1, x2 in x12:
        x13(f't={x1:.1f}, y={x2:.4f}')