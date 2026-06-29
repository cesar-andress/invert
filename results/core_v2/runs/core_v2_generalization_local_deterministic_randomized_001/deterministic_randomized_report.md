# INVERT Core v2 — F1.5 Deterministic/Randomized Report (`core_v2_generalization_local_deterministic_randomized_001`)

## 1. Generation validity (primary tasks)

- Generated artifacts: **120**
- Parsed at raw level: **120**
- Valid behavioral artifacts: **120**
- Invalid artifacts: **0**

## 2. Primary inter-execution variability recovery

Repeated `process_all()` runs with `seed=None`; classification uses trace identity only.

| strip_level | valid_detector_accuracy | valid_ambiguous_rate |
|-------------|-------------------------|----------------------|
| raw | 1.0000 | 0.0000 |
| format_normalized | 1.0000 | — |

## 3. Fixed-seed control collapse

Each artifact re-run 5 times with identical seed=12345 (`deterministic_randomized_fixed_seed_control.csv`). Randomized implementations should collapse to a single trace (detected as deterministic or ambiguous, not randomized).

- Randomized collapse rate (unique_trace_count == 1, raw): **1.0000**

## 4. Per-pole manipulation success (primary, valid artifacts, raw)

| requested method | manipulation_success_rate | rule |
|------------------|---------------------------|------|
| deterministic | 1.0000 | unique_trace_count == 1 under primary repeated runs |
| randomized | 1.0000 | unique_trace_count >= 2 under primary repeated runs |

## 5. Recovery conditioned on genuine poles (primary, raw)

| requested method | genuine_n | detector_accuracy |
|------------------|-----------|-------------------|
| deterministic (genuine only) | 60 | 1.0000 |
| randomized (genuine only) | 60 | 1.0000 |

## 6. Model ranking (valid-only primary recovery)

| rank | model | generated_n | valid_n | valid_artifact_rate | valid_accuracy_raw | valid_accuracy_format_normalized | valid_ambiguous_rate_raw | f1_5_survives |
|------|-------|-------------|---------|---------------------|---------------------|--------------------------------|--------------------------|---------------|
| 1 | Devstral:latest | 30 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |
| 2 | Qwen2.5-coder:14b | 30 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |
| 3 | Qwen2.5-coder:32b | 30 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |
| 4 | Qwen3-coder:30b | 30 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |

## 7. Local model conclusions

### Models supporting F1.5

- Devstral:latest, Qwen2.5-coder:14b, Qwen2.5-coder:32b, Qwen3-coder:30b

## 8. F1.5 decision (per model)

Preregistered rule: valid_n >= 20, valid_detector_accuracy >= 0.9 at raw and format_normalized, valid_ambiguous_rate <= 0.1.

### Inter-execution variability vs other signature classes

Deterministic and randomized implementations return the same item set and call visit_fn once per item; only repeated-execution trace stability differs.

## 9. All-generated summary

| model | task | method | strip_level | all_generated_n | accuracy | behavioral_pass | ambiguous |
|-------|------|--------|-------------|-----------------|----------|-----------------|-----------|
| ollama__devstral__latest | letters_8 | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | letters_8 | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | letters_8 | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | letters_8 | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | letters_8 | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | letters_8 | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | letters_8 | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | letters_8 | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | letters_8 | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | letters_8 | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_tokens | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_tokens | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_tokens | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_tokens | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_tokens | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_tokens | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_tokens | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_tokens | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_tokens | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | mixed_tokens | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | numbers_10 | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | numbers_10 | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | numbers_10 | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | numbers_10 | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | numbers_10 | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | numbers_10 | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | numbers_10 | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | numbers_10 | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | numbers_10 | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | numbers_10 | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | letters_8 | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | letters_8 | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | letters_8 | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | letters_8 | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | letters_8 | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | letters_8 | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | letters_8 | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | letters_8 | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | letters_8 | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | letters_8 | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_tokens | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_tokens | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_tokens | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_tokens | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_tokens | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_tokens | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_tokens | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_tokens | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_tokens | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | mixed_tokens | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | numbers_10 | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | numbers_10 | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | numbers_10 | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | numbers_10 | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | numbers_10 | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | numbers_10 | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | numbers_10 | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | numbers_10 | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | numbers_10 | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | numbers_10 | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | letters_8 | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | letters_8 | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | letters_8 | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | letters_8 | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | letters_8 | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | letters_8 | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | letters_8 | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | letters_8 | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | letters_8 | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | letters_8 | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_tokens | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_tokens | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_tokens | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_tokens | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_tokens | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_tokens | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_tokens | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_tokens | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_tokens | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | mixed_tokens | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | numbers_10 | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | numbers_10 | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | numbers_10 | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | numbers_10 | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | numbers_10 | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | numbers_10 | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | numbers_10 | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | numbers_10 | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | numbers_10 | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | numbers_10 | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | letters_8 | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | letters_8 | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | letters_8 | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | letters_8 | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | letters_8 | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | letters_8 | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | letters_8 | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | letters_8 | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | letters_8 | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | letters_8 | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_tokens | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_tokens | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_tokens | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_tokens | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_tokens | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_tokens | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_tokens | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_tokens | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_tokens | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | mixed_tokens | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | numbers_10 | deterministic | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | numbers_10 | deterministic | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | numbers_10 | deterministic | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | numbers_10 | deterministic | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | numbers_10 | deterministic | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | numbers_10 | randomized | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | numbers_10 | randomized | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | numbers_10 | randomized | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | numbers_10 | randomized | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | numbers_10 | randomized | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
