# Manifestation–Recovery Analysis

Run: `pilot_security_concurrency_001`
Observations: 120 artifact pairs (v0/v1)

## Taxonomy thresholds

Each observation is classified into exactly one category using fixed thresholds:

- **High manifestation**: `manifestation_score >= 0.1`
- **Low manifestation**: `manifestation_score < 0.1`
- **High recovery**: `recovery_correct >= 0.5` (mean accuracy across v0 and v1 artifacts)
- **Low recovery**: `recovery_correct < 0.5`

`manifestation_score` = mean of available components among:
`text_distance`, `ast_distance` (= 1 − `ast_similarity`),
`1 − import_jaccard`, `1 − function_jaccard`.

`recovery_correct` = mean of binary recovery outcomes for the v0 and v1 artifacts in the pair.

| Category | Label |
|----------|-------|
| A | High manifestation / High recovery |
| B | High manifestation / Low recovery |
| C | Low manifestation / High recovery |
| D | Low manifestation / Low recovery |

## 1. Does manifestation strongly predict recoverability?

- Pearson correlation (manifestation_score vs recovery_correct): **0.2804**
- Spearman correlation: **0.2521**

Pearson and Spearman magnitudes are below 0.3, indicating weak linear and monotonic association.
Recovery_correct is discrete ({0, 0.5, 1}) while manifestation_score is continuous;
this violates normality assumptions for Pearson correlation.
Spearman is more appropriate here but still shows weak association at this sample size (n=120).

## 2. Tasks with largest manifestation–recovery gap

Ranked by mean |manifestation_score − recovery_correct| (higher = stronger dissociation):

| Rank | Task | Mean gap | |gap| |
|------|------|----------|-------|
| 1 | rate_limiter | -0.4436 | 0.4436 |
| 2 | lru_cache | -0.4260 | 0.4260 |
| 3 | validate_email_like | -0.3413 | 0.3413 |
| 4 | merge_intervals | -0.3413 | 0.3413 |
| 5 | dependency_order | -0.1350 | 0.1350 |
| 6 | sanitize_filename | -0.1021 | 0.1021 |

## 3. Dimensions with largest manifestation–recovery gap

| Rank | Dimension | Mean gap | |gap| |
|------|-----------|----------|-------|
| 1 | security | -0.3130 | 0.3130 |
| 2 | concurrency | -0.2805 | 0.2805 |

## 4. Gap cases (Category B: high manifestation, low recovery)

Count: 0


## 5. Hallucinated recovery cases (Category C: low manifestation, high recovery)

Count: 22

- **dependency_order** | concurrency | openai | rep 1: manifestation_score=0.000000, text_distance=0.000000, ast_distance=0.000000, recovery_correct=0.500000, recovery_confidence=0.600000, keyword_correct=0.500000
- **dependency_order** | concurrency | openai | rep 2: manifestation_score=0.000000, text_distance=0.000000, ast_distance=0.000000, recovery_correct=0.500000, recovery_confidence=0.600000, keyword_correct=0.500000
- **dependency_order** | concurrency | openai | rep 3: manifestation_score=0.000000, text_distance=0.000000, ast_distance=0.000000, recovery_correct=0.500000, recovery_confidence=0.600000, keyword_correct=0.500000
- **dependency_order** | concurrency | openai | rep 4: manifestation_score=0.000000, text_distance=0.000000, ast_distance=0.000000, recovery_correct=0.500000, recovery_confidence=0.600000, keyword_correct=0.500000
- **dependency_order** | concurrency | openai | rep 5: manifestation_score=0.000000, text_distance=0.000000, ast_distance=0.000000, recovery_correct=0.500000, recovery_confidence=0.600000, keyword_correct=0.500000
- **validate_email_like** | concurrency | openai | rep 2: manifestation_score=0.000000, text_distance=0.000000, ast_distance=0.000000, recovery_correct=0.500000, recovery_confidence=0.550000, keyword_correct=0.500000
- **sanitize_filename** | security | anthropic | rep 1: manifestation_score=0.009534, text_distance=0.030953, ast_distance=0.007185, recovery_correct=0.500000, recovery_confidence=0.885000, keyword_correct=0.500000
- **merge_intervals** | concurrency | openai | rep 3: manifestation_score=0.011582, text_distance=0.046328, ast_distance=0.000000, recovery_correct=0.500000, recovery_confidence=0.625000, keyword_correct=0.500000
- **merge_intervals** | concurrency | openai | rep 4: manifestation_score=0.011582, text_distance=0.046328, ast_distance=0.000000, recovery_correct=0.500000, recovery_confidence=0.600000, keyword_correct=0.500000
- **merge_intervals** | concurrency | openai | rep 5: manifestation_score=0.011582, text_distance=0.046328, ast_distance=0.000000, recovery_correct=0.500000, recovery_confidence=0.600000, keyword_correct=0.500000
- **validate_email_like** | concurrency | anthropic | rep 1: manifestation_score=0.040569, text_distance=0.090483, ast_distance=0.071793, recovery_correct=0.500000, recovery_confidence=0.550000, keyword_correct=0.500000
- **validate_email_like** | concurrency | anthropic | rep 2: manifestation_score=0.040569, text_distance=0.090483, ast_distance=0.071793, recovery_correct=0.500000, recovery_confidence=0.550000, keyword_correct=0.500000
- **validate_email_like** | concurrency | anthropic | rep 3: manifestation_score=0.040569, text_distance=0.090483, ast_distance=0.071793, recovery_correct=0.500000, recovery_confidence=0.550000, keyword_correct=0.500000
- **validate_email_like** | concurrency | anthropic | rep 4: manifestation_score=0.040569, text_distance=0.090483, ast_distance=0.071793, recovery_correct=0.500000, recovery_confidence=0.550000, keyword_correct=0.500000
- **validate_email_like** | concurrency | anthropic | rep 5: manifestation_score=0.040569, text_distance=0.090483, ast_distance=0.071793, recovery_correct=0.500000, recovery_confidence=0.550000, keyword_correct=0.500000
- **sanitize_filename** | concurrency | openai | rep 1: manifestation_score=0.042670, text_distance=0.089494, ast_distance=0.081186, recovery_correct=0.500000, recovery_confidence=0.600000, keyword_correct=0.500000
- **sanitize_filename** | concurrency | openai | rep 5: manifestation_score=0.042670, text_distance=0.089494, ast_distance=0.081186, recovery_correct=0.500000, recovery_confidence=0.550000, keyword_correct=0.500000
- **lru_cache** | security | openai | rep 1: manifestation_score=0.043557, text_distance=0.113006, ast_distance=0.061224, recovery_correct=1.000000, recovery_confidence=0.780000, keyword_correct=0.500000
- **lru_cache** | security | openai | rep 4: manifestation_score=0.043557, text_distance=0.113006, ast_distance=0.061224, recovery_correct=1.000000, recovery_confidence=0.675000, keyword_correct=0.500000
- **lru_cache** | security | openai | rep 2: manifestation_score=0.063698, text_distance=0.170124, ast_distance=0.084669, recovery_correct=0.500000, recovery_confidence=0.600000, keyword_correct=0.500000
- **lru_cache** | security | openai | rep 5: manifestation_score=0.063698, text_distance=0.170124, ast_distance=0.084669, recovery_correct=0.500000, recovery_confidence=0.625000, keyword_correct=0.500000
- **lru_cache** | concurrency | openai | rep 1: manifestation_score=0.086598, text_distance=0.189711, ast_distance=0.156683, recovery_correct=0.500000, recovery_confidence=0.500000, keyword_correct=0.500000

## 6. Keyword baseline vs recovery in Category B subset

- No Category B observations; comparison not applicable.

## 7. Conclusion

Category counts: A=94, B=0, C=22, D=0.

**B.** Manifestation and recoverability show systematic dissociation. The manifestation–recovery gap deserves further investigation.
