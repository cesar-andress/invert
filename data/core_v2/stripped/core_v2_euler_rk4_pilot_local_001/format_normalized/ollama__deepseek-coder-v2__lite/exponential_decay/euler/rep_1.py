def x0(x1, x2):
    return -0.5 * x2

def x3(x0, x4, x5, x6, x7):
    x1 = x5
    x2 = x4
    x8 = [(x1, x2)]
    while x1 < x6:
        x2 += x7 * x0(x1, x2)
        x1 += x7
        x8.append((x1, x2))
    return x8
x4 = 1.0
x8 = x3(x0, x4, 0.0, 2.0, 0.1)
for x1, x2 in x8:
    x9(f't={x1}, y={x2}')