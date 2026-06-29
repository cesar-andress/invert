# Class C pole-asymmetry audit (`core_v2_generalization_local_eager_lazy_001`)

Read-only aggregation of existing partial-demand detection and full-demand control CSVs. No detectors, prompts, or validity metrics were modified.

## Partial-demand recovery by pole

| pole | generated_n | valid_n | genuine_n | manipulation_success_rate | detector_accuracy_raw | detector_accuracy_format_normalized | ambiguous_rate_raw | ambiguous_rate_format_normalized |
|------|-------------|---------|-----------|---------------------------|---------------------|--------------------------------|--------------------|--------------------------------|
| eager | 60 | 60 | 60 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |
| lazy | 60 | 60 | 60 | 1.0000 | 1.0000 | 0.7500 | 0.0000 | 0.2500 |

## Full-demand control by pole (raw, valid artifacts)

| pole | valid_n | detected_rate | ambiguous_rate | collapsed_rate |
|------|---------|---------------|----------------|----------------|
| eager | 60 | 1.0000 | 0.0000 | 0.0000 |
| lazy | 60 | 0.0000 | 1.0000 | 1.0000 |

Collapsed: for **lazy**, ambiguous under full demand; for **eager**, misclassified away from eager.

## Audit questions

### 1. Does partial-demand recovery hold for both poles?

**Yes at raw for both poles** (eager 1.0000, lazy 1.0000 valid-only detector accuracy). After format normalization, eager remains 1.0000 while lazy drops to 0.7500, so partial-demand recovery is **symmetric at raw** but **asymmetric under aggressive stripping**.

### 2. Is eager detected by a positive trace?

**Yes.** Eager artifacts are classified from a **positive precomputation trace**: all feature getters run before the first explicit request (`calls_before_first_request=3`, `unrequested_features_computed=true`).

### 3. Is lazy recovered by absence of unrequested computation?

**Yes.** Lazy recovery on partial demand relies on **absence of unrequested computation** (no features computed before the first getter; only `feature_a` on the first request).

### 4. Does lazy collapse under full demand?

**Yes for lazy, no for eager.** Under full-demand control, lazy collapses to ambiguous (1.0000 ambiguous / 1.0000 collapsed) while eager remains detected (1.0000 detected, 0.0000 ambiguous).

### 5. How should the paper phrase this conservatively?

Phrase conservatively that **Class C separates eager and lazy by temporal placement of the same computations**, not by different formulas: eager is supported by **observed early work**, lazy by **withheld work until demand**, and the lazy pole **weakens or collapses when all demand is front-loaded** (full-demand control). Report raw and stripped recovery separately; do not claim lazy is as strip-robust as eager.

