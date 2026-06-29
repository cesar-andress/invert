def f(t, y):
    K = 1.0
    r = 1.0
    return r * y * (1 - y / K)

def integrate_ode(f, y0, t0, tf, dt):
    y = y0
    t = t0
    result = [(t, y)]
    while t < tf:
        k1 = f(t, y)
        k2 = f(t + dt/2, y + dt*k1/2)
        k3 = f(t + dt/2, y + dt*k2/2)
        k4 = f(t + dt, y + dt*k3)
        y = y + dt * (k1 + 2*k2 + 2*k3 + k4) / 6
        t = t + dt
        result.append((t, y))
    return result

# Example usage
if __name__ == "__main__":
    y0 = 0.1
    t0 = 0.0
    tf = 2.0
    dt = 0.1
    solution = integrate_ode(f, y0, t0, tf, dt)
    for t, y in solution:
        print(f"t={t:.1f}, y={y:.4f}")