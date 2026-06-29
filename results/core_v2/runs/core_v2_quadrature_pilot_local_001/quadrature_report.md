# INVERT Core v2 — F1.2 Quadrature Report (`core_v2_quadrature_pilot_local_001`)

## 1. Generation validity

- Generated artifacts: **54**
- Parsed at raw level: **54**
- Valid behavioral artifacts: **54**
- Invalid artifacts (manipulation/validity failures): **0**

Invalid artifacts by model/task/method (raw level):

- None

Invalid artifacts are **not** recovery failures; they failed the behavioral oracle and are excluded from valid-only recovery metrics.

## 2. Model ranking (valid-only recovery)

| rank | model | generated_n | valid_n | valid_artifact_rate | valid_accuracy_raw | valid_accuracy_format_normalized | valid_ambiguous_rate_raw | f1_2_survives |
|------|-------|-------------|---------|---------------------|---------------------|--------------------------------|--------------------------|---------------|
| 1 | Qwen2.5-coder:14b | 18 | 18 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |
| 2 | Qwen2.5-coder:32b | 18 | 18 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |
| 3 | Qwen3-coder:30b | 18 | 18 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |

## 3. Local model conclusions

### Models supporting F1.2

- Qwen2.5-coder:14b, Qwen2.5-coder:32b, Qwen3-coder:30b

## 4. Recovery on valid artifacts only

| model | strip_level | valid_n | valid_detector_accuracy | valid_ambiguous_rate |
|-------|-------------|---------|-------------------------|----------------------|
| ollama__qwen2_5-coder__14b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | raw | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | raw | 3 | 1.0000 | 0.0000 |

## 5. F1.2 decision (per model)

Preregistered rule: valid_n >= 12, valid_detector_accuracy >= 0.9 at raw and format_normalized, valid_ambiguous_rate <= 0.1.

### Qwen2.5-coder:14b

**Yes.** Qwen2.5-coder:14b meets preregistered F1.2 thresholds on valid artifacts (valid_n=18, raw accuracy=1.0000, format_normalized accuracy=1.0000, ambiguous rate=0.0000).

### Qwen2.5-coder:32b

**Yes.** Qwen2.5-coder:32b meets preregistered F1.2 thresholds on valid artifacts (valid_n=18, raw accuracy=1.0000, format_normalized accuracy=1.0000, ambiguous rate=0.0000).

### Qwen3-coder:30b

**Yes.** Qwen3-coder:30b meets preregistered F1.2 thresholds on valid artifacts (valid_n=18, raw accuracy=1.0000, format_normalized accuracy=1.0000, ambiguous rate=0.0000).

### Should invalid artifacts be interpreted as recovery failure?

**No.** Invalid artifacts failed behavioral validation (parse/runtime/tolerance). They are manipulation/validity failures and must not enter valid-only recovery metrics.

## 6. All-generated summary (includes invalid artifacts)

| model | task | method | strip_level | all_generated_n | accuracy | behavioral_pass | ambiguous |
|-------|------|--------|-------------|-----------------|----------|-----------------|-----------|
| ollama__qwen2_5-coder__14b | integrate_exp_0_1 | simpson | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_exp_0_1 | simpson | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_exp_0_1 | simpson | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_exp_0_1 | simpson | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_exp_0_1 | simpson | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_exp_0_1 | trapezoidal | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_exp_0_1 | trapezoidal | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_exp_0_1 | trapezoidal | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_exp_0_1 | trapezoidal | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_exp_0_1 | trapezoidal | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_polynomial | simpson | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_polynomial | simpson | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_polynomial | simpson | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_polynomial | simpson | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_polynomial | simpson | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_polynomial | trapezoidal | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_polynomial | trapezoidal | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_polynomial | trapezoidal | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_polynomial | trapezoidal | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_polynomial | trapezoidal | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_sin_0_pi | simpson | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_sin_0_pi | simpson | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_sin_0_pi | simpson | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_sin_0_pi | simpson | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_sin_0_pi | simpson | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_sin_0_pi | trapezoidal | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_sin_0_pi | trapezoidal | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_sin_0_pi | trapezoidal | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_sin_0_pi | trapezoidal | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | integrate_sin_0_pi | trapezoidal | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_exp_0_1 | simpson | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_exp_0_1 | simpson | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_exp_0_1 | simpson | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_exp_0_1 | simpson | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_exp_0_1 | simpson | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_exp_0_1 | trapezoidal | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_exp_0_1 | trapezoidal | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_exp_0_1 | trapezoidal | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_exp_0_1 | trapezoidal | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_exp_0_1 | trapezoidal | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_polynomial | simpson | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_polynomial | simpson | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_polynomial | simpson | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_polynomial | simpson | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_polynomial | simpson | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_polynomial | trapezoidal | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_polynomial | trapezoidal | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_polynomial | trapezoidal | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_polynomial | trapezoidal | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_polynomial | trapezoidal | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_sin_0_pi | simpson | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_sin_0_pi | simpson | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_sin_0_pi | simpson | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_sin_0_pi | simpson | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_sin_0_pi | simpson | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_sin_0_pi | trapezoidal | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_sin_0_pi | trapezoidal | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_sin_0_pi | trapezoidal | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_sin_0_pi | trapezoidal | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | integrate_sin_0_pi | trapezoidal | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_exp_0_1 | simpson | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_exp_0_1 | simpson | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_exp_0_1 | simpson | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_exp_0_1 | simpson | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_exp_0_1 | simpson | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_exp_0_1 | trapezoidal | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_exp_0_1 | trapezoidal | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_exp_0_1 | trapezoidal | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_exp_0_1 | trapezoidal | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_exp_0_1 | trapezoidal | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_polynomial | simpson | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_polynomial | simpson | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_polynomial | simpson | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_polynomial | simpson | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_polynomial | simpson | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_polynomial | trapezoidal | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_polynomial | trapezoidal | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_polynomial | trapezoidal | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_polynomial | trapezoidal | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_polynomial | trapezoidal | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_sin_0_pi | simpson | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_sin_0_pi | simpson | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_sin_0_pi | simpson | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_sin_0_pi | simpson | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_sin_0_pi | simpson | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_sin_0_pi | trapezoidal | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_sin_0_pi | trapezoidal | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_sin_0_pi | trapezoidal | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_sin_0_pi | trapezoidal | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | integrate_sin_0_pi | trapezoidal | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
