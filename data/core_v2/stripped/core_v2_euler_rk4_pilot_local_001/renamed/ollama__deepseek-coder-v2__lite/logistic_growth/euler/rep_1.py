def x0(x1, x2):
    x3 = 1.0
    x4 = 1.0
    return x3 * x2 * (1 - x2 / x4)

def x5(x0, x6, x7, x8, x9):
    x1 = x7
    x2 = x6
    x10 = [(x1, x2)]
    while x1 < x8:
        x11 = x0(x1, x2) * x9
        x2 += x11
        x1 += x9
        x10.append((x1, x2))
    return x10
x6 = 0.1
x7 = 0.0
x8 = 2.0
x9 = 0.1
x10 = x5(x0, x6, x7, x8, x9)
for x1, x2 in x10:
    x12(f't={x1}, y={x2}')