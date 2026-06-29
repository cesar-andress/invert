def f(t, y):
    x, v = y
    omega = 1.0
    return [v, -omega ** 2 * x]

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    while t < tf:
        k1 = [dt * fi for fi in f(t, y)]
        k2 = [dt * fi for fi in f(t + 0.5 * dt, [yj + 0.5 * kj for yj, kj in zip(y, k1)])]
        k3 = [dt * fi for fi in f(t + 0.5 * dt, [yj + 0.5 * kj for yj, kj in zip(y, k2)])]
        k4 = [dt * fi for fi in f(t + dt, [yj + kj for yj, kj in zip(y, k3)])]
        y = [yj + (k1j + 2 * k2j + 2 * k3j + k4j) / 6.0 for yj, k1j, k2j, k3j, k4j in zip(y, k1, k2, k3, k4)]
        t += dt
    return y
y0 = [1.0, 0.0]
t0 = 0.0
tf = 2.0
dt = 0.05
result = integrate_ode(f, y0, t0, tf, dt)
print(result)