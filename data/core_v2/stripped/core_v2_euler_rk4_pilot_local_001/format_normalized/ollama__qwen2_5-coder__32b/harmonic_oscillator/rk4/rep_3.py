def x0(x1, x2):
    x3, x4 = x2
    x5 = 1.0
    return [x4, -x5 ** 2 * x3]

def x6(x0, x7, x8, x9, x10):
    x1 = x8
    x2 = x7
    while x1 < x9:
        x11 = [x10 * x12 for x12 in x0(x1, x2)]
        x13 = [x10 * x12 for x12 in x0(x1 + 0.5 * x10, [x14 + 0.5 * x15 for x14, x15 in x16(x2, x11)])]
        x17 = [x10 * x12 for x12 in x0(x1 + 0.5 * x10, [x14 + 0.5 * x15 for x14, x15 in x16(x2, x13)])]
        x18 = [x10 * x12 for x12 in x0(x1 + x10, [x14 + x15 for x14, x15 in x16(x2, x17)])]
        x2 = [x14 + (x19 + 2 * x20 + 2 * x21 + x22) / 6.0 for x14, x19, x20, x21, x22 in x16(x2, x11, x13, x17, x18)]
        x1 += x10
    return x2
x7 = [1.0, 0.0]
x8 = 0.0
x9 = 2.0
x10 = 0.05
x23 = x6(x0, x7, x8, x9, x10)
x24(x23)