def f(t, y):
    r = 1.0
    K = 1.0
    return r * y * (1 - y / K)

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    while t < tf:
        k1 = f(t, y)
        k2 = f(t + 0.5 * dt, y + 0.5 * dt * k1)
        k3 = f(t + 0.5 * dt, y + 0.5 * dt * k2)
        k4 = f(t + dt, y + dt * k3)
        y += dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt
    return y
y_final = integrate_ode(f, 0.1, 0.0, 2.0, 0.1)
print(y_final)