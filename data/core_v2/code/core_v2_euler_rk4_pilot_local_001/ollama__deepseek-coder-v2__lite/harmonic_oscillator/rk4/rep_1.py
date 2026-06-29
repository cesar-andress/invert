def f(t, y):
    x, v = y
    return [v, -omega**2 * x]

def integrate_ode(f, y0, t0, tf, dt):
    omega = 1.0
    h = dt
    n = int((tf - t0) / h)
    y = y0[:]
    for _ in range(n):
        k1 = f(t0, y)
        k2 = f(t0 + h/2, [y[i] + h*k1[i]/2 for i in range(len(y))])
        k3 = f(t0 + h/2, [y[i] + h*k2[i]/2 for i in range(len(y))])
        k4 = f(t0 + h, [y[i] + h*k3[i] for i in range(len(y))])
        y = [y[i] + (h/6)*(k1[i] + 2*k2[i] + 2*k3[i] + k4[i]) for i in range(len(y))]
        t0 += h
    return y

# Example usage:
y0 = [1.0, 0.0]
result = integrate_ode(f, y0, 0.0, 2.0, 0.05)
print(result)
