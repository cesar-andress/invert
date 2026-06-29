def x0(x1, x2):
    x3, x4 = x2
    x5 = 1.0
    x6 = x4
    x7 = -x5 ** 2 * x3
    return [x6, x7]

def x8(x0, x9, x10, x11, x12):
    x2 = x13(x9)
    x1 = x10
    x14 = [(x1, x2[0], x2[1])]
    while x1 < x11:
        x15 = x0(x1, x2)
        x2[0] += x12 * x15[0]
        x2[1] += x12 * x15[1]
        x1 += x12
        x14.append((x1, x2[0], x2[1]))
    return x14
x9 = [1.0, 0.0]
x10 = 0.0
x16 = 2.0
x12 = 0.05
x17 = x8(x0, x9, x10, x16, x12)