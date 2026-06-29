def f(t, y):
    r = 1.0
    K = 1.0
    return r * y * (1 - y / K)

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    while t < tf:
        k1 = f(t, y)
        k2 = f(t + 0.5 * dt, y + 0.5 * k1 * dt)
        k3 = f(t + 0.5 * dt, y + 0.5 * k2 * dt)
        k4 = f(t + dt, y + k3 * dt)
        y += (k1 + 2 * k2 + 2 * k3 + k4) * dt / 6
        t += dt
    return y

# Example usage:
y0 = 0.1
t0 = 0.0
tf = 2.0
dt = 0.1
result = integrate_ode(f, y0, t0, tf, dt)
print(result)
