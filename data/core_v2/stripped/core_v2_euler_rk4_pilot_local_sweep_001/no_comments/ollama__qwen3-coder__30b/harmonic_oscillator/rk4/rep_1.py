def f(t, y):
    x, v = y
    omega = 1.0
    dxdt = v
    dvdt = -omega ** 2 * x
    return [dxdt, dvdt]

def integrate_ode(f, y0, t0, tf, dt):
    y = list(y0)
    t = t0
    result = [(t, tuple(y))]
    while t < tf:
        k1 = f(t, y)
        k2 = f(t + dt / 2, [y[i] + dt * k1[i] / 2 for i in range(len(y))])
        k3 = f(t + dt / 2, [y[i] + dt * k2[i] / 2 for i in range(len(y))])
        k4 = f(t + dt, [y[i] + dt * k3[i] for i in range(len(y))])
        y = [y[i] + dt * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6 for i in range(len(y))]
        t += dt
        result.append((t, tuple(y)))
    return result
if __name__ == '__main__':
    y0 = [1.0, 0.0]
    t0 = 0.0
    tf = 2.0
    dt = 0.05
    solution = integrate_ode(f, y0, t0, tf, dt)
    print(solution)