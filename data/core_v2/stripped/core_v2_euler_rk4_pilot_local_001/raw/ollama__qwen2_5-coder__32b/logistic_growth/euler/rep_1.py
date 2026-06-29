def f(t, y):
    K = 1.0
    r = 1.0
    return r * y * (1 - y / K)

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    while t < tf:
        dydt = f(t, y)
        y += dt * dydt
        t += dt
    return y

# Example usage
y0 = 0.1
t0 = 0.0
tf = 2.0
dt = 0.1
result = integrate_ode(f, y0, t0, tf, dt)
print(result)