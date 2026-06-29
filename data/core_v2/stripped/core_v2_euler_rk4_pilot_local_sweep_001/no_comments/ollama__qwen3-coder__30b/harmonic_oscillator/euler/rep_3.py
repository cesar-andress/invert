def f(t, y):
    x, v = y
    omega = 1.0
    dxdt = v
    dvdt = -omega ** 2 * x
    return [dxdt, dvdt]

def integrate_ode(f, y0, t0, tf, dt):
    y = list(y0)
    t = t0
    result = [(t, y[0], y[1])]
    while t < tf:
        dy = f(t, y)
        y[0] += dt * dy[0]
        y[1] += dt * dy[1]
        t += dt
        result.append((t, y[0], y[1]))
    return result
y0 = [1.0, 0.0]
t0 = 0.0
t1 = 2.0
dt = 0.05
solution = integrate_ode(f, y0, t0, t1, dt)