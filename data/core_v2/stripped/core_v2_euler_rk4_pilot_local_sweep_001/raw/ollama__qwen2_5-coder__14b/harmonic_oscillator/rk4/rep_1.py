def f(t, y):
    x, v = y
    omega = 1.0
    return [v, -omega**2 * x]

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0[:]
    while t < tf:
        k1 = [dt * fi for fi in f(t, y)]
        k2 = [dt * fi for fi in f(t + 0.5 * dt, [y[i] + 0.5 * k1i for i, k1i in enumerate(k1)])]
        k3 = [dt * fi for fi in f(t + 0.5 * dt, [y[i] + 0.5 * k2i for i, k2i in enumerate(k2)])]
        k4 = [dt * fi for fi in f(t + dt, [y[i] + k3i for i, k3i in enumerate(k3)])]
        
        y = [yi + (k1i + 2 * k2i + 2 * k3i + k4i) / 6 for yi, k1i, k2i, k3i, k4i in zip(y, k1, k2, k3, k4)]
        t += dt
    return y

# Example usage:
y0 = [1.0, 0.0]
t0 = 0.0
tf = 2.0
dt = 0.05
result = integrate_ode(f, y0, t0, tf, dt)
print(result)