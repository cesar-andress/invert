# INVERT Core v2 — Cross-Run Decision Report

Aggregated from completed runs under `results/core_v2/runs/`. Missing per-run files are skipped gracefully.

Signature classes under evaluation:
- Class A: arithmetic count signatures (`euler_vs_rk4`)
- Class B: arithmetic weight signatures (`trapezoidal_vs_simpson`)
- Class C: dynamic temporal process signatures (`eager_vs_lazy`)

## Run inventory

### Development runs

- `core_v2_eager_lazy_pilot_local_001`
- `core_v2_euler_rk4_pilot_local_001`
- `core_v2_euler_rk4_pilot_local_sweep_001`
- `core_v2_quadrature_pilot_local_001`

### Frozen generalization runs

- `core_v2_generalization_local_quadrature_001` (has `frozen_detector_metadata.json`)

## 1. Which dimensions have enough evidence?

- Class A (derivative-call signatures)
- Class B (arithmetic weight signatures)
- Class C (dynamic temporal process signatures)

## 2. Which models are reliable generators?

- Devstral:latest
- Qwen2.5-coder:14b
- Qwen2.5-coder:32b
- Qwen3-coder:30b

## 3. Generation validity failures

- core_v2_euler_rk4_pilot_local_001 / DeepSeek-coder-v2:lite (euler_vs_rk4)
- core_v2_euler_rk4_pilot_local_sweep_001 / DeepSeek-coder-v2:lite (euler_vs_rk4)
- core_v2_euler_rk4_pilot_local_sweep_001 / Devstral:latest (euler_vs_rk4)
- core_v2_euler_rk4_pilot_local_sweep_001 / Qwen3-coder:30b (euler_vs_rk4)

## 4. Detector / stripping failures

- core_v2_eager_lazy_pilot_local_001 / Qwen3-coder:30b (eager_vs_lazy)

## 5. Is Class A supported?

**Yes (preliminary).** At least two models meet the preregistered valid-only survival rule for `euler_vs_rk4`.

## 6. Is Class B supported?

**Yes (preliminary).** At least two models meet the preregistered valid-only survival rule for `trapezoidal_vs_simpson`.

## 7. Is Class C supported?

**Yes (preliminary).** At least two models meet the preregistered valid-only survival rule for `eager_vs_lazy`.

## 8. Process signature vs mathematical identity (F1.3)

This result is not reducible to mathematical-coefficient identity because eager and lazy compute the same feature formulas; only timing of computation differs.

## 9. Two mechanistically distinct classes (preregistered criterion)

**Close.** Two mechanistically distinct classes each have >=2 surviving models under the preregistered valid-only rule; confirm with independent replication before strong claims.

## 10. Next cheapest experiment

Add the next preregistered Family 1 dimension or a minimal paid-API replication on the two best local models only.

## Dimension status snapshot

| dimension | runs_found | models_evaluated | models_survived | status |
|-----------|------------|------------------|-----------------|--------|
| euler_vs_rk4 | 2 | 5 | 2 | supported_if_2plus_models_survive |
| trapezoidal_vs_simpson | 2 | 4 | 4 | supported_if_2plus_models_survive |
| eager_vs_lazy | 1 | 4 | 3 | supported_if_2plus_models_survive |

## Frozen generalization evidence

### Class A (derivative-call signatures) (`euler_vs_rk4`)

- No frozen generalization runs analyzed for this dimension yet.

### Class B (arithmetic weight signatures) (`trapezoidal_vs_simpson`)

- Models evaluated: Devstral:latest, Qwen2.5-coder:14b, Qwen3-coder:30b
- Models survived: Devstral:latest, Qwen2.5-coder:14b, Qwen3-coder:30b
- Valid artifact rate: 1.0000
- Detector accuracy (raw): 1.0000
- Detector accuracy (format_normalized): 1.0000
- Ambiguous rate (raw): 0.0000

### Class C (dynamic temporal process signatures) (`eager_vs_lazy`)

- No frozen generalization runs analyzed for this dimension yet.

