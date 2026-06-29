# Strict Manifestation–Recovery Reanalysis

Run: `pilot_security_concurrency_001`

## 1. Recovery mean distribution

Complete pairs: 115

- recovery_mean = 0.5: **71** pairs
- recovery_mean = 1.0: **44** pairs

## 2. Strict recovery successes

- recovery_strict = 1 (both v0 and v1 correct): **44** / 115

## 3. Partial-only recoveries

- recovery_partial = 1 and recovery_strict = 0: **71**
- recovery_none = 1 (neither correct): **0**

## 4. Taxonomy change vs previous analysis

Previous thresholds: high recovery = recovery_mean >= 0.5.
Strict thresholds: high recovery = recovery_strict == 1.

| Category | Previous | Strict (all) | Strict (manipulation confirmed) |
|----------|----------|--------------|----------------------------------|
| A | 94 | 43 | 43 |
| B | 0 | 51 | 51 |
| C | 22 | 1 | 1 |
| D | 0 | 20 | 20 |

## 5. Does Category B now exist?

**Yes.** Category B count (all pairs): **51**. After manipulation_confirmed filter: **51**.

## 6. Does Category C survive?

Category C count (all pairs): **1** (previous: 22). After manipulation_confirmed filter: **1**.

## 7. After filtering to manipulation_confirmed == true

- Pairs retained: **115** / 115
- Category counts: A=43, B=51, C=1, D=20

- Pearson(manifestation_score, recovery_strict) on confirmed subset: **0.2977**

## 8. Is there still evidence for a manifestation–recovery gap?

Statistical checks (all complete pairs):

- Pearson(manifestation_score, recovery_mean): **0.2977**
- Pearson(manifestation_score, recovery_strict): **0.2977**
- Spearman(manifestation_score, recovery_strict): **0.2671**

Fisher 2×2 table (high_manifestation × recovery_strict):

| | recovery_strict=1 | recovery_strict=0 |
|---|---:|---:|
| manifestation >= 0.10 | 43 | 51 |
| manifestation < 0.10 | 1 | 20 |

Fisher exact p-value: **0.000316**

Category B contains 51 pairs where manifestation is high but strict recovery fails. This is the operational gap cell.

## 9. Does the previous conclusion survive?

The previous conclusion **does not survive in its original form**. Category C collapsed from 22 to 1 under strict recovery. However, Category B now contains **51** high-manifestation pairs that fail strict recovery — a real, stricter gap cell absent from the permissive taxonomy.

## Final conclusion

**C.** The previous interpretation weakens but a smaller, stricter gap remains.
