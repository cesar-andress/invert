# INVERT Core v2 — F1.1 Integration Report (`core_v2_euler_rk4_pilot_local_001`)

## 1. Generation validity

- Generated artifacts: **36**
- Parsed at raw level: **30**
- Valid behavioral artifacts: **24**
- Invalid artifacts (manipulation/validity failures): **12**

Invalid artifacts by model/task/method (raw level):

- `ollama__deepseek-coder-v2__lite/exponential_decay/euler`: 3
- `ollama__deepseek-coder-v2__lite/harmonic_oscillator/euler`: 3
- `ollama__deepseek-coder-v2__lite/harmonic_oscillator/rk4`: 3
- `ollama__deepseek-coder-v2__lite/logistic_growth/euler`: 3

Invalid artifacts are **not** recovery failures; they failed the behavioral oracle and are excluded from valid-only recovery metrics (R_raw, R_stripped).

## 2. Recovery on valid artifacts only

| model | strip_level | valid_n | valid_detector_accuracy | valid_ambiguous_rate |
|-------|-------------|---------|-------------------------|----------------------|
| ollama__deepseek-coder-v2__lite | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | raw | 3 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | format_normalized | 3 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | raw | 3 | 1.0000 | 0.0000 |
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

### Model aggregates (valid-only)

**DeepSeek-coder-v2:lite**
- raw: valid_n=6, accuracy=1.0000, ambiguous=0.0000
- format_normalized: valid_n=6, accuracy=1.0000, ambiguous=0.0000

**Qwen2.5-coder:32b**
- raw: valid_n=18, accuracy=1.0000, ambiguous=0.0000
- format_normalized: valid_n=18, accuracy=1.0000, ambiguous=0.0000

## 3. F1.1 decision

Preregistered rule: valid_n >= 12, valid_detector_accuracy >= 0.9 at raw and format_normalized, valid_ambiguous_rate <= 0.1.

### Does Qwen2.5-coder:32b support F1.1 survival after stripping?

**Yes.** Qwen2.5-coder:32b meets preregistered F1.1 thresholds on valid artifacts (valid_n=18, raw accuracy=1.0000, format_normalized accuracy=1.0000, ambiguous rate=0.0000).

### Does DeepSeek-coder-v2:lite support F1.1 survival after stripping?

**No / not yet.** DeepSeek-coder-v2:lite does not meet all F1.1 thresholds (valid_n=6, raw accuracy=1.0000, format_normalized accuracy=1.0000, ambiguous rate=0.0000).

### Should invalid artifacts be interpreted as recovery failure?

**No.** Invalid artifacts failed behavioral validation (parse/runtime/tolerance). They are manipulation/validity failures and must not enter R_raw or R_stripped.

### Is this enough to move to quadrature?

**Maybe.** One or more models meet valid-only F1.1 thresholds; review per-task failures and validity rates before expanding to quadrature.

## 4. All-generated summary (includes invalid artifacts)

Detector accuracy in this section includes invalid artifacts and is **not** used for F1.1 recovery decisions.

| model | task | method | strip_level | all_generated_n | accuracy | behavioral_pass | ambiguous |
|-------|------|--------|-------------|-----------------|----------|-----------------|-----------|
| ollama__deepseek-coder-v2__lite | exponential_decay | euler | format_normalized | 3 | 0.0000 | 0.0000 | 1.0000 |
| ollama__deepseek-coder-v2__lite | exponential_decay | euler | no_comments | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | exponential_decay | euler | no_imports | 3 | 0.0000 | 0.0000 | 1.0000 |
| ollama__deepseek-coder-v2__lite | exponential_decay | euler | raw | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | exponential_decay | euler | renamed | 3 | 0.0000 | 0.0000 | 1.0000 |
| ollama__deepseek-coder-v2__lite | exponential_decay | rk4 | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | exponential_decay | rk4 | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | exponential_decay | rk4 | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | exponential_decay | rk4 | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | exponential_decay | rk4 | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | harmonic_oscillator | euler | format_normalized | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | harmonic_oscillator | euler | no_comments | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | harmonic_oscillator | euler | no_imports | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | harmonic_oscillator | euler | raw | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | harmonic_oscillator | euler | renamed | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | harmonic_oscillator | rk4 | format_normalized | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | harmonic_oscillator | rk4 | no_comments | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | harmonic_oscillator | rk4 | no_imports | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | harmonic_oscillator | rk4 | raw | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | harmonic_oscillator | rk4 | renamed | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | logistic_growth | euler | format_normalized | 3 | 0.0000 | 0.0000 | 1.0000 |
| ollama__deepseek-coder-v2__lite | logistic_growth | euler | no_comments | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | logistic_growth | euler | no_imports | 3 | 0.0000 | 0.0000 | 1.0000 |
| ollama__deepseek-coder-v2__lite | logistic_growth | euler | raw | 3 | 1.0000 | 0.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | logistic_growth | euler | renamed | 3 | 0.0000 | 0.0000 | 1.0000 |
| ollama__deepseek-coder-v2__lite | logistic_growth | rk4 | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | logistic_growth | rk4 | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | logistic_growth | rk4 | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | logistic_growth | rk4 | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__deepseek-coder-v2__lite | logistic_growth | rk4 | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | exponential_decay | euler | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | exponential_decay | euler | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | exponential_decay | euler | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | exponential_decay | euler | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | exponential_decay | euler | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | exponential_decay | rk4 | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | exponential_decay | rk4 | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | exponential_decay | rk4 | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | exponential_decay | rk4 | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | exponential_decay | rk4 | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | harmonic_oscillator | euler | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | harmonic_oscillator | euler | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | harmonic_oscillator | euler | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | harmonic_oscillator | euler | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | harmonic_oscillator | euler | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | harmonic_oscillator | rk4 | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | harmonic_oscillator | rk4 | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | harmonic_oscillator | rk4 | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | harmonic_oscillator | rk4 | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | harmonic_oscillator | rk4 | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | logistic_growth | euler | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | logistic_growth | euler | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | logistic_growth | euler | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | logistic_growth | euler | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | logistic_growth | euler | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | logistic_growth | rk4 | format_normalized | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | logistic_growth | rk4 | no_comments | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | logistic_growth | rk4 | no_imports | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | logistic_growth | rk4 | raw | 3 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | logistic_growth | rk4 | renamed | 3 | 1.0000 | 1.0000 | 0.0000 |
