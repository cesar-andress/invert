def f(t, y):
    k = 0.5
    return -k * y

def integrate_ode(f, y0, t0, tf, dt):
    y = y0
    t = t0
    while t < tf:
        k1 = f(t, y)
        k2 = f(t + dt/2, y + dt*k1/2)
        k3 = f(t + dt/2, y + dt*k2/2)
        k4 = f(t + dt, y + dt*k3)
        y = y + dt*(k1 + 2*k2 + 2*k3 + k4)/6
        t = t + dt
    return y

# Test
result = integrate_ode(f, 1.0, 0.0, 2.0, 0.1)
print(result)
