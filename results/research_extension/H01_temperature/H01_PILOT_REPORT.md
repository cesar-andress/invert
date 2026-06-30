# H01 Temperature × Process Diversity — Pilot Report

**Study ID:** `H01_temperature_pilot`
**Generated (UTC):** 2026-06-30T11:36:50.376889+00:00

Literature-driven pilot (Lee et al. 2025; Hong et al. 2024). INVERT is the measuring instrument, not the validation object. No Core v2 frozen runs or detectors were modified.

## Preregistered scope

- Models: ollama:qwen2.5-coder:14b, ollama:qwen3-coder:30b
- Temperatures: (0.0, 0.4, 0.8)
- Repetitions: 10
- Classes: C, D, E

## Answers

### 1. Does temperature actually change process diversity?

**Partial / conditional.** 12 cells show >1 unique fingerprint (of 72 cells). See entropy_tables.csv.
- E letters_8 randomized ollama:qwen2.5-coder:14b T=0.0: unique=10/10 H=2.3026
- E numbers_10 randomized ollama:qwen2.5-coder:14b T=0.0: unique=10/10 H=2.3026
- E letters_8 randomized ollama:qwen2.5-coder:14b T=0.4: unique=10/10 H=2.3026
- E numbers_10 randomized ollama:qwen2.5-coder:14b T=0.4: unique=10/10 H=2.3026
- E letters_8 randomized ollama:qwen2.5-coder:14b T=0.8: unique=10/10 H=2.3026

### 2. Does recovery remain stable?

- ollama:qwen2.5-coder:14b class C: mean recovery=1.000, mean valid=1.000
- ollama:qwen2.5-coder:14b class D: mean recovery=0.500, mean valid=1.000
- ollama:qwen2.5-coder:14b class E: mean recovery=1.000, mean valid=1.000
- ollama:qwen3-coder:30b class C: mean recovery=1.000, mean valid=1.000
- ollama:qwen3-coder:30b class D: mean recovery=0.500, mean valid=1.000
- ollama:qwen3-coder:30b class E: mean recovery=1.000, mean valid=1.000

### 3. Is diversity confined to randomized Class E?

- only_e_randomized_diversity: **True** (0 diverse cells outside E:randomized)

### 4. Does perfect recovery mask richer process variation?

Recovery remains high while trace fingerprints stay monoculture on C/D; variation at E randomized is semantics-aligned, not hidden biodiversity.

### 5. Would this materially strengthen the TOSEM paper?

**no — would not materially strengthen TOSEM; abandon H01**

### 6. Should the complete H01 experiment be executed?

- **recommended:** `no-go`
- **full study:** False
- **reason:** abandon_h01_monoculture_except_e_randomized

## Go/no-go criteria

- criterion 1 (C/D CI increase, stable recovery): False
- criterion 2 (monotonic entropy): False []
- criterion 3 (model curve divergence): False

