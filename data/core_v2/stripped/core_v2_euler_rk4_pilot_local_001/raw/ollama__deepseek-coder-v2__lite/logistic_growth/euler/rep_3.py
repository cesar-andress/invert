def f(t, y):
    r = 1.0
    K = 1.0
    return r * y * (1 - y / K)

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    results = [(t, y)]
    while t < tf:
        dy = f(t, y) * dt
        y += dy
        t += dt
        results.append((t, y))
    return results

# Self-test using initial condition y0 = 0.1
y0 = 0.1
t0 = 0.0
tf = 2.0
dt = 0.1
results = integrate_ode(f, y0, t0, tf, dt)
for t, y in results:
    print(f"t={t:.2f}, y={y:.4f}")