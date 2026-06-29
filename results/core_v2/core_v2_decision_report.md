# INVERT Core v2 — Cross-Run Decision Report

Aggregated from completed runs under `results/core_v2/runs/`. Missing per-run files are skipped gracefully.

## 1. Which dimensions have enough evidence?

- Class A (derivative-call signatures)

## 2. Which models are reliable generators?

- Qwen2.5-coder:32b

## 3. Generation validity failures

- core_v2_euler_rk4_pilot_local_001 / DeepSeek-coder-v2:lite (euler_vs_rk4)

## 4. Detector / stripping failures

- None identified at the model-run aggregate level.

## 5. Is Class A supported?

**Partially.** One model meets the survival rule for `euler_vs_rk4`; a second independent survivor is still needed for strong support.

## 6. Is Class B supported?

Class B not yet evaluated.

## 7. Two mechanistically distinct classes (preregistered criterion)

**Not yet close.** Evidence exists for at least one class, but two independent classes with >=2 surviving models have not been demonstrated.

## 8. Next cheapest experiment

Run `invert-core analyze-run --run core_v2_quadrature_pilot_local_001` (or complete quadrature generation first) to evaluate Class B without new API spend.

## Dimension status snapshot

| dimension | runs_found | models_evaluated | models_survived | status |
|-----------|------------|------------------|-----------------|--------|
| euler_vs_rk4 | 1 | 2 | 1 | promising_if_1_model_survives |
| trapezoidal_vs_simpson | 0 | 0 | 0 | insufficient_data |
