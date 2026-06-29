def x0(x1, x2):
    x3 = 1.0
    x4, x5 = x2
    x6 = x5
    x7 = -x3 ** 2 * x4
    return [x6, x7]

def x8(x0, x9, x10, x11, x12):
    x1 = x10
    x2 = x13(x9)
    x14 = [(x1, x13(x2))]
    while x1 < x11:
        x15 = x0(x1, x2)
        for x16 in x17(x18(x2)):
            x2[x16] += x12 * x15[x16]
        x1 += x12
        x14.append((x1, x13(x2)))
    return x14
if x19 == '__main__':
    x9 = [1.0, 0.0]
    x10 = 0.0
    x11 = 2.0
    x12 = 0.05
    x20 = x8(x0, x9, x10, x11, x12)
    for x1, x2 in x20:
        x21(f't={x1:.2f}, x={x2[0]:.4f}, v={x2[1]:.4f}')