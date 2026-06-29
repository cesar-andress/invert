# Quadrature detector diagnosis (`core_v2_quadrature_pilot_local_001`)

Failed trapezoidal artifacts where the detector returned `ambiguous` or the wrong method.
The detector itself was not modified for this report.

## Failure classification counts

- **detector_too_strict**: 42
- **nonstandard_valid_trapezoidal**: 0
- **not_trapezoidal**: 0
- **stripping_broke_detector**: 81
- **ambiguous_legitimate**: 0

## Interpretation guide

### detector_too_strict

Generated code appears to implement trapezoidal quadrature correctly, but rigid signature rules (separate half weights, return * h) missed it.

### nonstandard_valid_trapezoidal

Behaviorally valid trapezoidal implementations using unconventional structure (n+1 sample grid, indexed arrays, late *= h scaling).

### not_trapezoidal

Code is not trapezoidal or failed the behavioral oracle without recoverable trapezoidal signatures.

### stripping_broke_detector

Raw/no_comments detection was stronger; renaming or import stripping changed scope or introduced false Simpson cues.

### ambiguous_legitimate

Ambiguous classification is reasonable given weak or mixed arithmetic signatures.

## Examples: detector_too_strict

### ollama__qwen2_5-coder__14b / integrate_exp_0_1 / rep_1 / raw

- detected: `ambiguous`
- behavioral_pass: `true`
- notes: Uses 0.5*(f(a)+f(b)) endpoint averaging; detector expects separate half weights.

```python
def integrate(f, a, b, n):
    h = (b - a) / n
    integral = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        integral += f(a + i * h)
    return integral * h
```

### ollama__qwen2_5-coder__14b / integrate_exp_0_1 / rep_1 / no_comments

- detected: `ambiguous`
- behavioral_pass: `true`
- notes: Uses 0.5*(f(a)+f(b)) endpoint averaging; detector expects separate half weights.

```python
def integrate(f, a, b, n):
    h = (b - a) / n
    integral = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        integral += f(a + i * h)
    return integral * h
```

### ollama__qwen2_5-coder__14b / integrate_exp_0_1 / rep_2 / raw

- detected: `ambiguous`
- behavioral_pass: `true`
- notes: Uses 0.5*(f(a)+f(b)) endpoint averaging; detector expects separate half weights.

```python
def integrate(f, a, b, n):
    h = (b - a) / n
    integral = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        integral += f(a + i * h)
    return integral * h
```

### ollama__qwen2_5-coder__14b / integrate_exp_0_1 / rep_2 / no_comments

- detected: `ambiguous`
- behavioral_pass: `true`
- notes: Uses 0.5*(f(a)+f(b)) endpoint averaging; detector expects separate half weights.

```python
def integrate(f, a, b, n):
    h = (b - a) / n
    integral = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        integral += f(a + i * h)
    return integral * h
```

### ollama__qwen2_5-coder__14b / integrate_exp_0_1 / rep_3 / raw

- detected: `ambiguous`
- behavioral_pass: `true`
- notes: Uses 0.5*(f(a)+f(b)) endpoint averaging; detector expects separate half weights.

```python
def integrate(f, a, b, n):
    h = (b - a) / n
    integral = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        integral += f(a + i * h)
    return integral * h
```

## Examples: stripping_broke_detector

### ollama__qwen2_5-coder__14b / integrate_exp_0_1 / rep_1 / renamed

- detected: `ambiguous`
- behavioral_pass: `true`
- notes: Detection regressed after stripping or entry-function scope changed.

```python
def x0(x1, x2, x3, x4):
    x5 = (x3 - x2) / x4
    x6 = 0.5 * (x1(x2) + x1(x3))
    for x7 in x8(1, x4):
        x6 += x1(x2 + x7 * x5)
    return x6 * x5
```

### ollama__qwen2_5-coder__14b / integrate_exp_0_1 / rep_1 / no_imports

- detected: `ambiguous`
- behavioral_pass: `true`
- notes: Detection regressed after stripping or entry-function scope changed.

```python
def x0(x1, x2, x3, x4):
    x5 = (x3 - x2) / x4
    x6 = 0.5 * (x1(x2) + x1(x3))
    for x7 in x8(1, x4):
        x6 += x1(x2 + x7 * x5)
    return x6 * x5
```

### ollama__qwen2_5-coder__14b / integrate_exp_0_1 / rep_1 / format_normalized

- detected: `ambiguous`
- behavioral_pass: `true`
- notes: Detection regressed after stripping or entry-function scope changed.

```python
def x0(x1, x2, x3, x4):
    x5 = (x3 - x2) / x4
    x6 = 0.5 * (x1(x2) + x1(x3))
    for x7 in x8(1, x4):
        x6 += x1(x2 + x7 * x5)
    return x6 * x5
```

### ollama__qwen2_5-coder__14b / integrate_exp_0_1 / rep_2 / renamed

- detected: `ambiguous`
- behavioral_pass: `true`
- notes: Detection regressed after stripping or entry-function scope changed.

```python
def x0(x1, x2, x3, x4):
    x5 = (x3 - x2) / x4
    x6 = 0.5 * (x1(x2) + x1(x3))
    for x7 in x8(1, x4):
        x6 += x1(x2 + x7 * x5)
    return x6 * x5
```

### ollama__qwen2_5-coder__14b / integrate_exp_0_1 / rep_2 / no_imports

- detected: `ambiguous`
- behavioral_pass: `true`
- notes: Detection regressed after stripping or entry-function scope changed.

```python
def x0(x1, x2, x3, x4):
    x5 = (x3 - x2) / x4
    x6 = 0.5 * (x1(x2) + x1(x3))
    for x7 in x8(1, x4):
        x6 += x1(x2 + x7 * x5)
    return x6 * x5
```

