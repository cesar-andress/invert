def f(t, y):
    k = 0.5
    return -k * y

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    while t < tf:
        y += dt * f(t, y)
        t += dt
    return y

# Example usage
y0 = 1.0
t0 = 0.0
tf = 2.0
dt = 0.1
result = integrate_ode(f, y0, t0, tf, dt)
print(result)