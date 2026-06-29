def f(t, y):
    k = 0.5
    return -k * y

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    results = [(t, y)]

    while t < tf:
        y_new = y + dt * f(t, y)
        t += dt
        y = y_new
        results.append((t, y))

    return results

# Self-test with the given parameters
if __name__ == "__main__":
    y0 = 1.0
    t0 = 0.0
    tf = 2.0
    dt = 0.1
    result = integrate_ode(f, y0, t0, tf, dt)
    for t, y in result:
        print(f"t={t:.1f}, y={y:.4f}")