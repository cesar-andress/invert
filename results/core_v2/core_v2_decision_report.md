# INVERT Core v2 — Cross-Run Decision Report

Aggregated from completed runs under `results/core_v2/runs/`. Missing per-run files are skipped gracefully.

## Run inventory

### Development runs

- `core_v2_euler_rk4_pilot_local_001`
- `core_v2_euler_rk4_pilot_local_sweep_001`
- `core_v2_quadrature_pilot_local_001`

### Frozen generalization runs

- None yet.

## 1. Which dimensions have enough evidence?

- Class A (derivative-call signatures)
- Class B (arithmetic weight signatures)

## 2. Which models are reliable generators?

- Qwen2.5-coder:14b
- Qwen2.5-coder:32b
- Qwen3-coder:30b

## 3. Generation validity failures

- core_v2_euler_rk4_pilot_local_001 / DeepSeek-coder-v2:lite (euler_vs_rk4)
- core_v2_euler_rk4_pilot_local_sweep_001 / DeepSeek-coder-v2:lite (euler_vs_rk4)
- core_v2_euler_rk4_pilot_local_sweep_001 / Devstral:latest (euler_vs_rk4)
- core_v2_euler_rk4_pilot_local_sweep_001 / Qwen3-coder:30b (euler_vs_rk4)

## 4. Detector / stripping failures

- None identified at the model-run aggregate level.

## 5. Is Class A supported?

**Yes (preliminary).** At least two models meet the preregistered valid-only survival rule for `euler_vs_rk4`.

## 6. Is Class B supported?

**Yes (preliminary).** At least two models meet the preregistered valid-only survival rule for `trapezoidal_vs_simpson`.

## 7. Two mechanistically distinct classes (preregistered criterion)

**Close.** Two mechanistically distinct classes each have >=2 surviving models under the preregistered valid-only rule; confirm with independent replication before strong claims.

## 8. Next cheapest experiment

Add the next preregistered Family 1 dimension or a minimal paid-API replication on the two best local models only.

## Dimension status snapshot

| dimension | runs_found | models_evaluated | models_survived | status |
|-----------|------------|------------------|-----------------|--------|
| euler_vs_rk4 | 2 | 5 | 2 | supported_if_2plus_models_survive |
| trapezoidal_vs_simpson | 1 | 3 | 3 | supported_if_2plus_models_survive |

## Frozen generalization evidence

### Class A (derivative-call signatures) (`euler_vs_rk4`)

- No frozen generalization runs analyzed for this dimension yet.

### Class B (arithmetic weight signatures) (`trapezoidal_vs_simpson`)

- No frozen generalization runs analyzed for this dimension yet.

