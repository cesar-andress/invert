"""Integrate dy/dt = -y from t0 to tf using classic RK4 (four f evaluations per step)."""


def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    while t < tf:
        k1 = f(t, y)
        k2 = f(t + dt / 2, y + dt / 2 * k1)
        k3 = f(t + dt / 2, y + dt / 2 * k2)
        k4 = f(t + dt, y + dt * k3)
        y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t = t + dt
    return y
