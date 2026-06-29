def f(t, y):
    omega = 1.0
    x, v = y
    dxdt = v
    dvdt = -omega**2 * x
    return [dxdt, dvdt]

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = list(y0)
    results = [(t, list(y))]

    while t < tf:
        k1 = [dt * fi for fi in f(t, y)]
        k2 = [dt * fi for fi in f(t + 0.5*dt, [yj + 0.5*kj for yj, kj in zip(y, k1)])]
        k3 = [dt * fi for fi in f(t + 0.5*dt, [yj + 0.5*kj for yj, kj in zip(y, k2)])]
        k4 = [dt * fi for fi in f(t + dt, [yj + kj for yj, kj in zip(y, k3)])]

        y = [yj + (k1j + 2*k2j + 2*k3j + k4j)/6 for yj, k1j, k2j, k3j, k4j in zip(y, k1, k2, k3, k4)]
        t += dt
        results.append((t, list(y)))

    return results

# Self-test example
if __name__ == "__main__":
    y0 = [1.0, 0.0]
    t0 = 0.0
    tf = 2.0
    dt = 0.05
    results = integrate_ode(f, y0, t0, tf, dt)
    for t, y in results:
        print(f"t={t:.2f}, x={y[0]:.4f}, v={y[1]:.4f}")