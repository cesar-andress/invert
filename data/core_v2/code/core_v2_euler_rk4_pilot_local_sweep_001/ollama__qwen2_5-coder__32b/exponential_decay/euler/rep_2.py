def f(t, y):
    k = 0.5
    return -k * y

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    while t < tf:
        dydt = f(t, y)
        y += dydt * dt
        t += dt
    return y

# Example usage
y_final = integrate_ode(f, 1.0, 0.0, 2.0, 0.1)
print(y_final)
