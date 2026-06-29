def x0(x1, x2):
    x3 = 0.5
    return -x3 * x2

def x4(x0, x5, x6, x7, x8):
    x2 = x5
    x1 = x6
    x9 = [(x1, x2)]
    while x1 < x7:
        x2 = x2 + x8 * x0(x1, x2)
        x1 = x1 + x8
        x9.append((x1, x2))
    return x9
if x10 == '__main__':
    x11 = x4(x0, 1.0, 0.0, 2.0, 0.1)
    for x1, x2 in x11:
        x12(f't={x1:.1f}, y={x2:.6f}')