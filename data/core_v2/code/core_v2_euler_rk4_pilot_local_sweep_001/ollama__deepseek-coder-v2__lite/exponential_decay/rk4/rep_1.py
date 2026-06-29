def f(t, y):
    return -0.5 * y

def integrate_ode(f, y0, t0, tf, dt):
    nsteps = int((tf - t0) / dt)
    y = y0
    for _ in range(nsteps):
        k1 = f(t0, y)
        k2 = f(t0 + 0.5 * dt, y + 0.5 * dt * k1)
        k3 = f(t0 + 0.5 * dt, y + 0.5 * dt * k2)
        k4 = f(t0 + dt, y + dt * k3)
        y += (dt / 6) * (k1 + 2*k2 + 2*k3 + k4)
        t0 += dt
    return y

# Self-test with initial condition y0 = 1.0
y_final = integrate_ode(f, 1.0, 0.0, 2.0, 0.1)
print(y_final)  # Expected to be close to 0.36787944117144233
