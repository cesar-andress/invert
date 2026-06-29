def f(t, y):
    return -0.5 * y

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    results = [(t, y)]
    while t < tf:
        y += dt * f(t, y)
        t += dt
        results.append((t, y))
    return results

# Example usage:
results = integrate_ode(f, 1.0, 0.0, 2.0, 0.1)
for t, y in results:
    print(f"t={t}, y={y}")