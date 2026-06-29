def x0(x1, x2):
    x3, x4 = x2
    x5 = 1.0
    x6 = x4
    x7 = -x5 ** 2 * x3
    return [x6, x7]

def x8(x0, x9, x10, x11, x12):
    x2 = x13(x9)
    x1 = x10
    x14 = [(x1, x15(x2))]
    while x1 < x11:
        x16 = x0(x1, x2)
        x17 = x0(x1 + x12 / 2, [x2[x18] + x12 * x16[x18] / 2 for x18 in x19(x20(x2))])
        x21 = x0(x1 + x12 / 2, [x2[x18] + x12 * x17[x18] / 2 for x18 in x19(x20(x2))])
        x22 = x0(x1 + x12, [x2[x18] + x12 * x21[x18] for x18 in x19(x20(x2))])
        x2 = [x2[x18] + x12 * (x16[x18] + 2 * x17[x18] + 2 * x21[x18] + x22[x18]) / 6 for x18 in x19(x20(x2))]
        x1 += x12
        x14.append((x1, x15(x2)))
    return x14
if x23 == '__main__':
    x9 = [1.0, 0.0]
    x10 = 0.0
    x11 = 2.0
    x12 = 0.05
    x24 = x8(x0, x9, x10, x11, x12)
    x25(x24)