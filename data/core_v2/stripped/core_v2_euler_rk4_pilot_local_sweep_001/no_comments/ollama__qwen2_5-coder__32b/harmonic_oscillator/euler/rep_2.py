def f(t, y):
    x, v = y
    omega = 1.0
    return [v, -omega ** 2 * x]

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = list(y0)
    while t < tf:
        dydt = f(t, y)
        y[0] += dt * dydt[0]
        y[1] += dt * dydt[1]
        t += dt
    return y
y0 = [1.0, 0.0]
t0 = 0.0
tf = 2.0
dt = 0.05
result = integrate_ode(f, y0, t0, tf, dt)
print(result)