# INVERT Core v2 — F1.3 Full-Demand Control (`core_v2_generalization_local_eager_lazy_001`)

Validity control: all getters (`get_feature_a/b/c`) are requested before classification. When no avoidable unrequested computation remains, lazy timing signatures should collapse and overall recovery should drop relative to partial demand.

## Recovery comparison (valid artifacts only)

| condition | strip_level | valid_detector_accuracy | valid_ambiguous_rate |
|-----------|-------------|-------------------------|----------------------|
| partial demand | raw | 1.0000 | 0.0000 |
| partial demand | format_normalized | 0.8750 | — |
| full demand control | raw | 0.5000 | 0.5000 |
| full demand control | format_normalized | 0.5000 | — |

## Interpretation

- **Control passed (directional):** full-demand recovery is lower than partial-demand, consistent with discrimination relying on avoidable unrequested computation.

## Per-method full-demand outcomes (raw, valid artifacts)

| requested method | valid_n | detector_accuracy | ambiguous_rate |
|------------------|---------|-------------------|----------------|
| eager | 60 | 1.0000 | 0.0000 |
| lazy | 60 | 0.0000 | 1.0000 |
