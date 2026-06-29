def f(t, y):
    k = 0.5
    return -k * y

def integrate_ode(f, y0, t0, tf, dt):
    y = y0
    t = t0
    results = [(t, y)]

    while t < tf:
        k1 = f(t, y)
        k2 = f(t + 0.5 * dt, y + 0.5 * dt * k1)
        k3 = f(t + 0.5 * dt, y + 0.5 * dt * k2)
        k4 = f(t + dt, y + dt * k3)

        y = y + (dt / 6) * (k1 + 2*k2 + 2*k3 + k4)
        t += dt
        results.append((t, y))

    return results

# Self-test example
if __name__ == "__main__":
    y0 = 1.0
    t0 = 0.0
    tf = 2.0
    dt = 0.1
    result = integrate_ode(f, y0, t0, tf, dt)
    for t, y in result:
        print(f"t={t:.1f}, y={y:.6f}")