def f(t, y):
    k = 0.5
    return -k * y

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
    solution = integrate_ode(f, 1.0, 0.0, 2.0, 0.1)
    for t, y in solution:
        print(f"t={t:.1f}, y={y:.6f}")