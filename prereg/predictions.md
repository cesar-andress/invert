# INVERT Core v2 — Preregistered Predictions

## Primary claim

Some process intents leave objectively recoverable **process signatures** in generated
artifacts after lexical/API stripping, verifiable by deterministic detectors without
human annotators.

## F1.1 Euler vs RK4 (integration method)

| Prediction | Value |
|------------|-------|
| Detector accuracy on manipulation-confirmed pairs | ≥ 0.90 |
| Detection survives `no_comments`, `renamed`, `format_normalized` | ≥ 0.95 of confirmed pairs |
| Detection survives `no_imports` | ≥ 0.90 (no import dependency) |
| Manipulation failure rate (behavioral pass, detector abstain) | ≤ 0.10 |

## F2.1 Lock vs no-lock (positive trivial control)

| Prediction | Value |
|------------|-------|
| Detector accuracy | ≥ 0.95 |
| False positive rate on no-lock artifacts | ≤ 0.05 |

## F3.2 Shuffled-label negative control

| Prediction | Value |
|------------|-------|
| Recovery/detection accuracy vs shuffled labels | 0.40 – 0.60 (at chance) |
| Must reject if accuracy ≥ 0.70 on shuffled labels |

## Not tested

- LLM judge failure does **not** imply absence of process signature.
- Non-identifiability of stylistic intent dimensions (Family 2/3 legacy).
