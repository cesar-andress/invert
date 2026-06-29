def f(t, y):
    K = 1.0
    r = 1.0
    return r * y * (1 - y / K)

def integrate_ode(f, y0, t0, tf, dt):
    y = y0
    t = t0
    result = [(t, y)]
    while t < tf:
        y = y + dt * f(t, y)
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