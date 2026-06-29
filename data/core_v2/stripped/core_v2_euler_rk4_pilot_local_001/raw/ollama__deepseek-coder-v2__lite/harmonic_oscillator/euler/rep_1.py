def f(t, y):
    x, v = y
    return [v, -omega**2 * x]

def integrate_ode(f, y0, t0, tf, dt):
    omega = 1.0
    steps = int((tf - t0) / dt)
    y = y0[:]
    for _ in range(steps):
        dy = f(t0, y)
        y[0] += dy[0] * dt
        y[1] += dy[1] * dt
        t0 += dt
    return y

# Self-test with initial conditions y0 = [1.0, 0.0]
y0 = [1.0, 0.0]
result = integrate_ode(f, y0, 0.0, 2.0, 0.05)
print(result)