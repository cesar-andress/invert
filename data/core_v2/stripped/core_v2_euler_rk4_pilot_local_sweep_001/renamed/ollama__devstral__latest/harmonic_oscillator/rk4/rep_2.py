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
        x15 = [x12 * x16 for x16 in x0(x1, x2)]
        x17 = [x12 * x16 for x16 in x0(x1 + 0.5 * x12, [x18 + 0.5 * x19 for x18, x19 in x20(x2, x15)])]
        x21 = [x12 * x16 for x16 in x0(x1 + 0.5 * x12, [x18 + 0.5 * x19 for x18, x19 in x20(x2, x17)])]
        x22 = [x12 * x16 for x16 in x0(x1 + x12, [x18 + x19 for x18, x19 in x20(x2, x21)])]
        x2 = [x18 + (x23 + 2 * x24 + 2 * x25 + x26) / 6 for x18, x23, x24, x25, x26 in x20(x2, x15, x17, x21, x22)]
        x1 += x12
        x14.append((x1, x13(x2)))
    return x14
if x27 == '__main__':
    x9 = [1.0, 0.0]
    x10 = 0.0
    x11 = 2.0
    x12 = 0.05
    x14 = x8(x0, x9, x10, x11, x12)
    for x1, x2 in x14:
        x28(f't={x1:.2f}, x={x2[0]:.4f}, v={x2[1]:.4f}')