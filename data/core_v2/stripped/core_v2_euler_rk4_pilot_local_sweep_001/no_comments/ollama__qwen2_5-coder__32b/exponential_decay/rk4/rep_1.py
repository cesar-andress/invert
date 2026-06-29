def f(t, y):
    k = 0.5
    return -k * y

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    while t < tf:
        k1 = dt * f(t, y)
        k2 = dt * f(t + 0.5 * dt, y + 0.5 * k1)
        k3 = dt * f(t + 0.5 * dt, y + 0.5 * k2)
        k4 = dt * f(t + dt, y + k3)
        y += (k1 + 2 * k2 + 2 * k3 + k4) / 6
        t += dt
    return y
y_final = integrate_ode(f, 1.0, 0.0, 2.0, 0.1)
print(y_final)