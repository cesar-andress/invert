# External Variability Study — Analysis Plan

**Study ID:** RQ-EXT-E  
**Protocol:** `EXTERNAL_VARIABILITY_PROTOCOL.md`  
**Schema:** `external_variability_results_schema.csv`  
**Status:** Frozen before scoring

---

## 1. Analysis tiers

| Tier | Population | Use |
|------|------------|-----|
| **Primary** | Generated artifacts with `one_shot_pass = true` | RQ1, RQ2, RQ3 model vs reference |
| **Secondary** | All parsed generated artifacts | Parsing and invalid rates |
| **Reference** | `canonical_solution` per task | RQ3 baseline; harness sanity |
| **Excluded** | Tasks in `task_exclusions.csv` | Reporting only |

Confirmatory INVERT Core v2 metrics are **never** pooled with this study.

---

## 2. Primary endpoints (RQ mapping)

### RQ1 — Prevalence of variability

**Endpoint:** `variable_rate = variable_n / valid_n`

- `variable_n`: count with `variability_label = variable`
- 95% CI: Wilson score interval for binomial proportion
- Report alongside `stable_rate` and `flaky_rate`

**Secondary descriptive:** distribution of `unique_output_hash_count` among valid artifacts (histogram in appendix).

### RQ2 — Beyond one-shot pass

**Endpoints:**

| Metric | Definition |
|--------|------------|
| `hidden_variability_rate` | `(one_shot_pass_and_variable) / valid_n` |
| `hidden_flaky_rate` | `(one_shot_pass_and_flaky) / valid_n` |
| `one_shot_only_pass_rate` | `valid_n / parsed_n` |

**Contrast table (appendix):**

| Gate | Variable | Flaky |
|------|----------|-------|
| One-shot pass only | — | — |
| Repeated execution | count | count |

Optional: compare one-shot pass on **base HumanEval tests** vs **EvalPlus augmented** (if harness exports both) to show augmented gate strictly tighter; report separately, not as primary endpoint unless prespecified before pilot.

### RQ3 — Group comparison

**Groups:**

| `source_group` | Members |
|----------------|---------|
| `local_llm` | Four Ollama models (per protocol) |
| `commercial_llm` | API models if run; else omitted |
| `reference` | HumanEval+ canonical solutions |

**Endpoints per group:** `stable_rate`, `variable_rate`, `flaky_rate` with 95% CIs.

**Comparisons (descriptive):**

- Each local model vs `reference` (difference in proportions + CI)
- Pooled `local_llm` vs `reference`
- If commercial run: `commercial_llm` vs pooled `local_llm`

**No multiplicity correction** required for exploratory study; report all intervals transparently.

---

## 3. Confidence intervals

### 3.1 Binomial (primary)

For proportion `p = k/n`:

- Method: **Wilson score interval** at 95%
- Implementation: `scipy.stats.binomtest` or equivalent; document in analysis script
- If `n = 0`, report “not applicable”

### 3.2 Bootstrap (sensitivity)

- Unit of resample: artifacts (task_id, model_id) with replacement
- Resamples: 10,000
- Bootstrap RNG seed: **42** (analysis only; not solution execution)
- Report 2.5th and 97.5th percentiles for `variable_rate`, `stable_rate`
- Use when `valid_n < 100` for a group to corroborate Wilson intervals

### 3.3 Effect size

For group A vs B on `variable_rate`:

- Report **absolute difference** `p_A - p_B` with 95% CI (Newcombe hybrid or bootstrap)
- Report **risk ratio** `p_A / p_B` only if `p_B > 0.01`; otherwise omit ratio to avoid instability

No p-values in main appendix table unless journal requires; prefer CIs.

---

## 4. Aggregate tables (prespecified)

### Table E1 — Study flow

| Stage | n |
|-------|---|
| Tasks included | |
| Tasks excluded | |
| `generated_n` | |
| `parsed_n` | |
| `valid_n` | |
| `invalid_n` | |

### Table E2 — Variability labels (valid only)

| Label | n | % of valid |
|-------|---|------------|
| stable | | |
| variable | | |
| flaky_invalid | | |
| timeout | | |
| error | | |
| ambiguous | | |

### Table E3 — Rates by model (valid only)

Columns: `model_id`, `valid_n`, `stable_rate` (CI), `variable_rate` (CI), `flaky_rate` (CI)

### Table E4 — Reference baseline

Same as E3 for `source_group = reference`

### Table E5 — RQ2 hidden risk

`one_shot_pass_and_variable`, `one_shot_pass_and_flaky` counts and rates

---

## 5. Sanity checks (halt rules)

Before reporting generated results:

1. **Reference stability:** `stable_rate` for reference ≥ 0.95. If not, stop and fix harness.
2. **Detector SHA256** matches `detector_freeze.json`.
3. **No detector file changes** since freeze commit.
4. **Task exclusion log** complete.

---

## 6. Uncertainty and small-sample policy

| Condition | Reporting rule |
|-----------|----------------|
| `valid_n ≥ 100` per group | Report Wilson CI; bootstrap optional |
| `30 ≤ valid_n < 100` | Report Wilson CI; label **moderate precision** |
| `valid_n < 30` | Report point estimate + Wilson CI; label **low precision**; no subgroup claims |
| `variable_n < 5` | Do not interpret pairwise differences as meaningful |

---

## 7. Claims guardrails (analysis)

Analysis scripts must **not** emit:

- External validation of Class C/D/E recovery
- Pole recovery rates
- “INVERT generalizes” language

Allowed summary strings (templates):

- “Among EvalPlus-valid completions on HumanEval+, `variable_rate = X%` (95% CI: …).”
- “`hidden_variability_rate = Y%` passed one-shot tests but showed output instability under 10 repeated executions.”
- “Reference solutions were `stable` in Z% of tasks (harness sanity).”

---

## 8. Software deliverables (analysis phase)

| Script | Output |
|--------|--------|
| `scripts/analyze_external_variability.py` (to be written at Phase 3) | Tables E1–E5 |
| `results/external_variability/summary_by_model.csv` | Machine-readable aggregates |
| `results/external_variability/analysis_report.md` | Narrative + CIs |

**Not implemented in protocol phase** — analysis runs only after Phase 2 sweep.

---

## 9. Optional sensitivity analyses (appendix only)

Prespecified; not headline:

1. **N = 20** subsample (if primary run used N = 10): rerun detector on random 50% of valid artifacts with N = 20; compare label agreement.
2. **Fixed-seed arm:** `random.seed(0)` wrapper; separate table.
3. **Base HumanEval vs EvalPlus** one-shot pass rates.

---

## 10. Timeline

| Step | Depends on |
|------|------------|
| Lock protocol | Done |
| Phase 1 pilot | Harness |
| Phase 2 sweep | Phase 1 pass |
| Run this analysis plan | Phase 2 CSV |
| Draft manuscript inserts | Analysis complete |
