# INVERT Core v2 — F1.3 Eager/Lazy Report (`core_v2_generalization_local_eager_lazy_001`)

## 1. Generation validity

- Generated artifacts: **120**
- Parsed at raw level: **120**
- Valid behavioral artifacts: **120**
- Invalid artifacts (manipulation/validity failures): **0**

Invalid artifacts by model/task/method (raw level):

- None

Invalid artifacts are **not** recovery failures; they failed the behavioral oracle and are excluded from valid-only recovery metrics.

## 2. Normal partial-demand recovery

Detector requests only `get_feature_a` before classification (primary F1.3 condition).

| strip_level | valid_detector_accuracy | valid_ambiguous_rate |
|-------------|-------------------------|----------------------|
| raw | 1.0000 | 0.0000 |
| format_normalized | 0.8750 | — |

## 3. Full-demand control recovery

All getters requested before classification (`eager_lazy_full_demand_control.csv`). Lazy pole should become largely non-recoverable when no avoidable computation remains.

| strip_level | valid_detector_accuracy | valid_ambiguous_rate |
|-------------|-------------------------|----------------------|
| raw | 0.5000 | 0.5000 |
| format_normalized | 0.5000 | — |

## 4. Per-pole manipulation success (partial demand, valid artifacts, raw)

| requested method | manipulation_success_rate | rule |
|------------------|---------------------------|------|
| eager | 1.0000 | all features computed before first getter |
| lazy | 1.0000 | no unrequested feature computed before/during first getter |

## 5. Recovery conditioned on genuine poles (partial demand, raw)

| requested method | genuine_n | detector_accuracy |
|------------------|-----------|-------------------|
| eager (genuine eager only) | 60 | 1.0000 |
| lazy (genuine lazy only) | 60 | 1.0000 |

## 6. Model ranking (valid-only partial-demand recovery)

| rank | model | generated_n | valid_n | valid_artifact_rate | valid_accuracy_raw | valid_accuracy_format_normalized | valid_ambiguous_rate_raw | f1_3_survives |
|------|-------|-------------|---------|---------------------|---------------------|--------------------------------|--------------------------|---------------|
| 1 | Devstral:latest | 30 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |
| 2 | Qwen2.5-coder:14b | 30 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |
| 3 | Qwen2.5-coder:32b | 30 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |
| 4 | Qwen3-coder:30b | 30 | 30 | 1.0000 | 1.0000 | 0.5000 | 0.0000 | fail |

## 7. Local model conclusions

### Models supporting F1.3

- Devstral:latest, Qwen2.5-coder:14b, Qwen2.5-coder:32b

## 8. Recovery on valid artifacts only (partial demand)

| model | strip_level | valid_n | valid_detector_accuracy | valid_ambiguous_rate |
|-------|-------------|---------|-------------------------|----------------------|
| ollama__devstral__latest | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__devstral__latest | raw | 5 | 1.0000 | 0.0000 |
| ollama__devstral__latest | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__devstral__latest | raw | 5 | 1.0000 | 0.0000 |
| ollama__devstral__latest | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__devstral__latest | raw | 5 | 1.0000 | 0.0000 |
| ollama__devstral__latest | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__devstral__latest | raw | 5 | 1.0000 | 0.0000 |
| ollama__devstral__latest | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__devstral__latest | raw | 5 | 1.0000 | 0.0000 |
| ollama__devstral__latest | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__devstral__latest | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 5 | 0.0000 | 1.0000 |
| ollama__qwen3-coder__30b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 5 | 0.0000 | 1.0000 |
| ollama__qwen3-coder__30b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 5 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | raw | 5 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 5 | 0.0000 | 1.0000 |
| ollama__qwen3-coder__30b | raw | 5 | 1.0000 | 0.0000 |

## 9. F1.3 decision (per model, partial demand)

Preregistered rule: valid_n >= 20, valid_detector_accuracy >= 0.9 at raw and format_normalized, valid_ambiguous_rate <= 0.1.

### Devstral:latest

**Yes.** Devstral:latest meets preregistered F1.3 thresholds on valid artifacts (valid_n=30, raw accuracy=1.0000, format_normalized accuracy=1.0000, ambiguous rate=0.0000).

### Qwen2.5-coder:14b

**Yes.** Qwen2.5-coder:14b meets preregistered F1.3 thresholds on valid artifacts (valid_n=30, raw accuracy=1.0000, format_normalized accuracy=1.0000, ambiguous rate=0.0000).

### Qwen2.5-coder:32b

**Yes.** Qwen2.5-coder:32b meets preregistered F1.3 thresholds on valid artifacts (valid_n=30, raw accuracy=1.0000, format_normalized accuracy=1.0000, ambiguous rate=0.0000).

### Qwen3-coder:30b

**No / not yet.** Qwen3-coder:30b does not meet all F1.3 thresholds (valid_n=30, raw accuracy=1.0000, format_normalized accuracy=0.5000, ambiguous rate=0.0000).

### Should invalid artifacts be interpreted as recovery failure?

**No.** Invalid artifacts failed behavioral validation (parse/runtime/correctness). They are manipulation/validity failures and must not enter valid-only recovery metrics.

### Process signature vs mathematical identity

Eager and lazy variants compute the same feature formulas; only the timing of callback invocation differs. Successful F1.3 recovery therefore supports dynamic temporal process signatures beyond static arithmetic identity.

## 10. All-generated summary (includes invalid artifacts)

| model | task | method | strip_level | all_generated_n | accuracy | behavioral_pass | ambiguous |
|-------|------|--------|-------------|-----------------|----------|-----------------|-----------|
| ollama__devstral__latest | mixed_signed_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_signed_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_signed_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_signed_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_signed_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_signed_vector | lazy | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_signed_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_signed_vector | lazy | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_signed_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_signed_vector | lazy | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | repeated_values_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | repeated_values_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | repeated_values_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | repeated_values_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | repeated_values_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | repeated_values_vector | lazy | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | repeated_values_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | repeated_values_vector | lazy | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | repeated_values_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | repeated_values_vector | lazy | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | small_positive_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | small_positive_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | small_positive_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | small_positive_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | small_positive_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | small_positive_vector | lazy | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | small_positive_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | small_positive_vector | lazy | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | small_positive_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | small_positive_vector | lazy | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_signed_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_signed_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_signed_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_signed_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_signed_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_signed_vector | lazy | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_signed_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_signed_vector | lazy | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_signed_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_signed_vector | lazy | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | repeated_values_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | repeated_values_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | repeated_values_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | repeated_values_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | repeated_values_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | repeated_values_vector | lazy | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | repeated_values_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | repeated_values_vector | lazy | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | repeated_values_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | repeated_values_vector | lazy | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | small_positive_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | small_positive_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | small_positive_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | small_positive_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | small_positive_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | small_positive_vector | lazy | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | small_positive_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | small_positive_vector | lazy | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | small_positive_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | small_positive_vector | lazy | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_signed_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_signed_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_signed_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_signed_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_signed_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_signed_vector | lazy | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_signed_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_signed_vector | lazy | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_signed_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_signed_vector | lazy | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | repeated_values_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | repeated_values_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | repeated_values_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | repeated_values_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | repeated_values_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | repeated_values_vector | lazy | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | repeated_values_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | repeated_values_vector | lazy | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | repeated_values_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | repeated_values_vector | lazy | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | small_positive_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | small_positive_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | small_positive_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | small_positive_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | small_positive_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | small_positive_vector | lazy | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | small_positive_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | small_positive_vector | lazy | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | small_positive_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | small_positive_vector | lazy | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_signed_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_signed_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_signed_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_signed_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_signed_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_signed_vector | lazy | format_normalized | 5 | 0.0000 | 1.0000 | 1.0000 |
| ollama__qwen3-coder__30b | mixed_signed_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_signed_vector | lazy | no_imports | 5 | 0.0000 | 1.0000 | 1.0000 |
| ollama__qwen3-coder__30b | mixed_signed_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_signed_vector | lazy | renamed | 5 | 0.0000 | 1.0000 | 1.0000 |
| ollama__qwen3-coder__30b | repeated_values_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | repeated_values_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | repeated_values_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | repeated_values_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | repeated_values_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | repeated_values_vector | lazy | format_normalized | 5 | 0.0000 | 1.0000 | 1.0000 |
| ollama__qwen3-coder__30b | repeated_values_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | repeated_values_vector | lazy | no_imports | 5 | 0.0000 | 1.0000 | 1.0000 |
| ollama__qwen3-coder__30b | repeated_values_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | repeated_values_vector | lazy | renamed | 5 | 0.0000 | 1.0000 | 1.0000 |
| ollama__qwen3-coder__30b | small_positive_vector | eager | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | small_positive_vector | eager | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | small_positive_vector | eager | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | small_positive_vector | eager | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | small_positive_vector | eager | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | small_positive_vector | lazy | format_normalized | 5 | 0.0000 | 1.0000 | 1.0000 |
| ollama__qwen3-coder__30b | small_positive_vector | lazy | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | small_positive_vector | lazy | no_imports | 5 | 0.0000 | 1.0000 | 1.0000 |
| ollama__qwen3-coder__30b | small_positive_vector | lazy | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | small_positive_vector | lazy | renamed | 5 | 0.0000 | 1.0000 | 1.0000 |
