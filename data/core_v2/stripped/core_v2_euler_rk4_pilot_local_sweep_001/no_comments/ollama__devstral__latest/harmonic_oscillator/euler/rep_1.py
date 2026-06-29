def f(t, y):
    omega = 1.0
    x, v = y
    dxdt = v
    dvdt = -omega ** 2 * x
    return [dxdt, dvdt]

def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = list(y0)
    results = [(t, list(y))]
    while t < tf:
        dy = f(t, y)
        for i in range(len(y)):
            y[i] += dt * dy[i]
        t += dt
        results.append((t, list(y)))
    return results
if __name__ == '__main__':
    y0 = [1.0, 0.0]
    t0 = 0.0
    tf = 2.0
    dt = 0.05
    solution = integrate_ode(f, y0, t0, tf, dt)
    for t, y in solution:
        print(f't={t:.2f}, x={y[0]:.4f}, v={y[1]:.4f}')