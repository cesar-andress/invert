def f(t, y):
    r = 1.0
    K = 1.0
    return r * y * (1 - y / K)

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0

    while t < tf:
        y_new = y + dt * f(t, y)
        t += dt
        y = y_new

    return y

# Self-test example
y_final = integrate_ode(f, 0.1, 0.0, 2.0, 0.1)
print(f"Final value of y at t={2.0}: {y_final}")
