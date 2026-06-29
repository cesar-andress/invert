"""Integrate dy/dt = -y from t0 to tf using forward Euler (one f evaluation per step)."""


def integrate_ode(f, y0, t0, tf, dt):
    t = t0
    y = y0
    while t < tf:
        y = y + dt * f(t, y)
        t = t + dt
    return y
