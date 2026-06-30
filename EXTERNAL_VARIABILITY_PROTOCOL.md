# External Variability Study: Inter-Execution Reproducibility on Independent Benchmarks

**Study ID:** `RQ-EXT-E`  
**Protocol version:** 1.0  
**Protocol date:** 2026-06-30  
**Status:** Preregistered / frozen before external corpus scoring  
**Artifact repository:** `~/papers/invert/invert`

---

## 0. Scope and non-goals

This protocol defines an **exploratory** external study separate from INVERT Core v2 confirmatory runs. It does **not**:

- modify or reuse the frozen Class E detector (`deterministic_randomized.py`);
- validate pole recovery for Classes C, D, or E on external code;
- claim interface-agnostic recovery for quantity, order, or variability poles;
- substitute for trace-contract benchmarks in the main Results section.

It **does** measure whether functionally valid solutions on an independent Python benchmark exhibit **inter-execution output instability** under repeated execution, using the frozen **external output-stability detector**.

**Frozen detector (do not modify after protocol lock):**

| Field | Value |
|-------|-------|
| Module | `invert_core.external.external_variability_detector` |
| Path | `src/invert_core/external/external_variability_detector.py` |
| SHA256 | `bf247dfdf1b57c16d460f643418cdf1bd893ef6218b4bca06b05a202ee830d6c` |
| Freeze record | `results/external_variability/detector_freeze.json` |
| Uses INVERT API | **No** |

Companion docs: `EXTERNAL_VARIABILITY_DETECTOR_PROTOCOL.md`, `configs/external_variability_protocol.yaml`, `external_variability_analysis_plan.md`.

---

## 1. Research questions

### RQ1 — Prevalence

How often do **functionally valid** generated Python solutions on an independent benchmark exhibit **inter-execution variability** under repeated execution?

**Operationalization:** among artifacts that pass the benchmark test suite on the first full validation pass, what fraction receive detector label `variable` (more than one unique normalized output hash across N runs)?

### RQ2 — Beyond one-shot tests

Does inter-execution variability identify **reproducibility risks not captured by one-shot functional tests**?

**Operationalization:** count artifacts with `one_shot_pass = true` that are classified `variable` or `flaky_invalid` on repeated execution. Report the conditional rate and example task IDs (appendix only; no cherry-picking).

### RQ3 — Group comparison

How do **local models**, **commercial models** (if run), and **human/reference** solutions differ in stability rates?

**Operationalization:** compare `stable_rate`, `variable_rate`, and `flaky_rate` among valid artifacts by `source_group` ∈ {`local_llm`, `commercial_llm`, `reference`} with uncertainty intervals (Section 8).

---

## 2. Dataset selection (frozen)

### 2.1 Primary dataset

**HumanEval+** (EvalPlus-augmented HumanEval)

| Property | Value |
|----------|-------|
| Source | OpenAI HumanEval + EvalPlus augmented tests (`evalplus` package; Liu et al., NeurIPS 2023) |
| Language | Python |
| Task count | 164 (HumanEval base; EvalPlus test augmentation) |
| Execution model | Function-call with bundled test inputs |
| Reference solutions | `canonical_solution` field available per task |
| Rationale | Best ROI per feasibility memo; already cited in manuscript; supports RQ2 via stronger one-shot gate vs base HumanEval |

**Frozen identifier:** `humaneval_plus_v1`

### 2.2 Secondary datasets (out of scope for v1.0 protocol)

Deferred unless a prespecified extension amendment is written **before** scoring:

| Dataset | Status |
|---------|--------|
| MBPP sanitized (377) | Extension replication only |
| MBPP full | Extension only |
| EffiBench-X Python subset | Deprioritized (stdin/Docker friction; prior external probes) |
| INVERT Family 1 | **Excluded** (internal trace-contract benchmark) |

### 2.3 Task inclusion rules

Include a task only if **all** hold:

1. Python implementation with automatic executable tests.
2. Runner can invoke the entry function without interactive stdin.
3. EvalPlus/HumanEval oracle can judge pass/fail automatically.
4. Task does not **explicitly** require nondeterministic output as the correct answer unless the bundled tests encode equivalence automatically (none expected on HumanEval+).

### 2.4 Task exclusion rules

Exclude and log in `results/external_variability/task_exclusions.csv` if any hold:

| Code | Reason |
|------|--------|
| `non_python` | Not Python |
| `no_automatic_tests` | No runnable test bundle |
| `interactive_input` | Requires interactive stdin not supported by runner |
| `nondeterminism_allowed` | Prompt/spec allows multiple valid outputs without automated equivalence |
| `runner_incompatible` | Harness cannot extract callable entry point |
| `pilot_failed` | Pilot harness error on reference solution (documented) |

**No post-hoc task dropping** after seeing model variability rates.

---

## 3. Generation and prompting

### 3.1 Models (planned)

**Local (primary; reuse existing Ollama stack):**

| Model ID | Notes |
|----------|-------|
| `ollama:qwen2.5-coder:14b` | Frozen generalization tier |
| `ollama:qwen2.5-coder:32b` | Frozen generalization tier |
| `ollama:qwen3-coder:30b` | Frozen generalization tier |
| `ollama:devstral:latest` | Frozen generalization tier |

Generation settings: `temperature = 0`, same as Core v2 generalization configs.

**Commercial (optional; budget permitting, max 2):**

| Model ID | Provider | Notes |
|----------|----------|-------|
| `openai:gpt-4o-mini` | OpenAI | Listed in `configs/models.yaml` |
| `anthropic:claude-3-5-sonnet-20241022` | Anthropic | Optional second API |

Commercial runs are **separate** from Core v2 confirmatory aggregates. If not executed, RQ3 compares `local_llm` vs `reference` only.

### 3.2 Completions per (task, model)

| Parameter | Value |
|-----------|-------|
| Completions | 1 per (task_id, model_id) |
| Parsing | Extract first valid Python function body per EvalPlus convention |
| `generated_n` | tasks × models attempted |
| `parsed_n` | completions with extractable code |

### 3.3 Prompt template (frozen)

Use the **original HumanEval problem statement** and function signature only.

**Required:**

- Standard HumanEval docstring + `def` signature from dataset.
- Instruction to complete the function body.

**Forbidden in prompts:**

- Naming process poles (eager/lazy, BFS/DFS, deterministic/randomized).
- Requesting randomness or reproducibility.
- Mentioning INVERT, trace contracts, or visit functions.
- Asking for deterministic or randomized behavior.

**Example skeleton (conceptual):**

```
Complete the following Python function. Return only the function implementation.

{prompt from dataset}
```

No model-specific prompt tuning after pilot.

---

## 4. Human and reference comparison

For every included HumanEval+ task, run the **same** frozen detector on:

| `source_group` | Source |
|----------------|--------|
| `reference` | Dataset `canonical_solution` |

Reference solutions are **not** included in generated-model denominators but are reported alongside for RQ3.

**Expected baseline:** reference solutions should be predominantly `stable` (sanity check). If reference instability rate exceeds 5%, halt and document harness/environment issue before scoring generated artifacts.

---

## 5. Functional validation

### 5.1 One-shot gate

Before repeated-execution analysis:

1. Run the **full** EvalPlus-augmented test suite once on the artifact.
2. Record `one_shot_pass` (boolean).
3. If fail → label `invalid_functional`; exclude from valid-only variability denominators.
4. Record failure reason category when available (`syntax`, `runtime`, `assertion`, `timeout`).

### 5.2 Valid-only repeated execution

Only artifacts with `one_shot_pass = true` enter RQ1–RQ3 valid-only rates.

Invalid artifacts are counted separately (`invalid_n`) and never silently dropped.

---

## 6. Repeated execution protocol

### 6.1 Run count

| Parameter | Value |
|-----------|-------|
| Primary `N` | **10** repeated executions per valid artifact per task input bundle |
| Optional `N` | **20** only if pilot median wall time per artifact &lt; 200 ms and total sweep &lt; 24 h |

`N` is frozen in `configs/external_variability_protocol.yaml` before the full sweep. Do not change `N` after seeing variability rates.

### 6.2 Input bundle

- Use EvalPlus/HumanEval official test inputs for the task (frozen per task_id).
- Same arguments for all N runs within an artifact.
- One bundle per task unless dataset specifies multiple official entry invocations (record `bundle_id`).

### 6.3 Detector execution

Invoke `analyze_external_variability()` from the frozen detector module with:

- `protocol` loaded from `configs/external_variability_protocol.yaml`
- `entry_point` = HumanEval `entry_point` field
- `validators` = EvalPlus test predicate per bundle (pass/fail only)

**Classification labels (frozen):** `stable`, `variable`, `flaky_invalid`, `timeout`, `error`, `ambiguous` (see `EXTERNAL_VARIABILITY_DETECTOR_PROTOCOL.md`).

### 6.4 Randomness and seed policy

**Primary evaluation (RQ1–RQ3):**

- **Do not** inject `random.seed(...)` into the runner or solution namespace.
- **Do not** instruct models to use fixed seeds in prompts.
- Generation uses `temperature = 0` (model sampling policy only).
- Reflect **normal execution behavior** of the submitted code under repeated calls.

**Environment controls (documented, not solution seeding):**

| Variable | Primary value | Purpose |
|----------|---------------|---------|
| `TZ` | `UTC` | Timestamp consistency in logs |
| `PYTHONHASHSEED` | unset (system default) | Do not force unless sensitivity arm run |

**Optional sensitivity arm (separate, not mixed into primary rates):**

- Label: `fixed_seed_sensitivity`
- Procedure: wrap execution with `random.seed(0)` before each of N runs (or once per process, documented).
- Report in appendix table only; **not** merged into headline RQ1–RQ3 rates.

### 6.5 Environment documentation

Record in `results/external_variability/run_environment.json`:

- Python version
- OS / kernel
- `evalplus` package version
- Git commit of invert repo
- Detector SHA256
- Ollama version (if local)
- Date of sweep

### 6.6 Timeouts

| Parameter | Value |
|-----------|-------|
| Per-run timeout | 2.0 s (`timeout_sec` in protocol YAML) |
| One-shot validation timeout | 5.0 s per task (harness) |

---

## 7. Metrics and outputs

### 7.1 Per-artifact fields

See `external_variability_results_schema.csv`. Key fields:

- Identifiers: `study_id`, `dataset`, `task_id`, `model_id`, `source_group`, `artifact_id`
- Gate: `one_shot_pass`, `externally_valid`
- Detector: `variability_label`, `unique_output_hash_count`, `pass_count`, `fail_count`, `timeout_count`, `error_count`, `ambiguous_count`
- RQ2: `one_shot_pass_and_variable`, `one_shot_pass_and_flaky`

### 7.2 Aggregate metrics

Computed over generated artifacts unless noted:

| Metric | Definition |
|--------|------------|
| `generated_n` | Generation attempts |
| `parsed_n` | Successfully parsed completions |
| `valid_n` | `one_shot_pass = true` |
| `invalid_n` | `parsed_n - valid_n` |
| `stable_n` | valid with label `stable` |
| `variable_n` | valid with label `variable` |
| `flaky_invalid_n` | valid with label `flaky_invalid` |
| `timeout_n` | label `timeout` |
| `error_n` | label `error` |
| `ambiguous_n` | label `ambiguous` |
| `stable_rate` | `stable_n / valid_n` |
| `variable_rate` | `variable_n / valid_n` |
| `flaky_rate` | `flaky_invalid_n / valid_n` |

Report **per-model** and **reference** breakdowns for RQ3.

### 7.3 Output files (frozen paths)

| Path | Content |
|------|---------|
| `results/external_variability/artifacts.csv` | Per-artifact rows |
| `results/external_variability/summary_by_model.csv` | Aggregates |
| `results/external_variability/summary_reference.csv` | Reference baseline |
| `results/external_variability/task_exclusions.csv` | Excluded tasks |
| `results/external_variability/run_environment.json` | Environment |
| `results/external_variability/protocol_lock.json` | Protocol SHA256 + commit |

---

## 8. Statistical analysis

See `external_variability_analysis_plan.md`. Summary:

- Binomial 95% Wilson intervals for `stable_rate`, `variable_rate`, `flaky_rate` per group.
- Bootstrap 95% CI (10,000 resamples, seed 42 for bootstrap only) as sensitivity check.
- Pairwise group comparisons: difference in proportions with CI; no p-value fishing.
- Minimum reporting threshold: if `valid_n < 30` for a model, report point estimate but flag **low precision** in text.
- No claim of significance without reporting uncertainty.

---

## 9. Claims policy

### 9.1 Allowed claims

- The external detector measures inter-execution **output stability** without INVERT trace contracts.
- On HumanEval+, functionally valid generated solutions **do or do not** exhibit measurable repeated-execution variability at reported rates.
- Variability/flakiness highlights reproducibility risks **not captured by a single functional pass** (RQ2), with counts and examples.
- Local models differ from reference solutions in stability rates **on this benchmark** (RQ3), with uncertainty.

### 9.2 Forbidden claims

- All INVERT classes generalize externally.
- Classes C or D are externally validated.
- Arbitrary production-code validity.
- Universal process-signature recovery.
- Interface-agnostic recovery for **all** dimensions (quantity, order, variability).
- Process Trinity completeness or pole recovery on external code.
- Confirmatory equivalence to frozen Class E recovery rates.

---

## 10. Manuscript placement

- **Not** in main confirmatory Results alongside Class C/D/E recovery tables.
- **Allowed:** Threats to Validity paragraph, Limitations, Data Availability pointer, Appendix table/figure.
- Draft text: `manuscript_section_external_variability_draft.tex`, `updated_threats_for_external_variability_draft.tex`.

---

## 11. Execution phases (do not skip)

| Phase | Action | Gate |
|-------|--------|------|
| 0 | Protocol locked (this document + detector SHA256) | Complete |
| 1 | Harness pilot: 10 tasks × reference + 1 local model | Reference stable ≥ 95% |
| 2 | Full generation + sweep | Frozen `N`, frozen detector |
| 3 | Analysis per plan | No detector changes |
| 4 | Manuscript appendix text | Exploratory framing only |

**Do not run Phase 2 until Phase 1 passes.**

---

## 12. Freeze checklist

- [x] Detector implemented and smoke-tested
- [x] Detector SHA256 recorded (`detector_freeze.json`)
- [x] This protocol written
- [x] Results schema defined
- [x] Analysis plan written
- [ ] Harness pilot (Phase 1) — **not started**
- [ ] Full sweep (Phase 2) — **not started**

**After Phase 0 lock:** do not modify `external_variability_detector.py` or classification rules.

---

## 13. Related repository artifacts

| File | Role |
|------|------|
| `EXTERNAL_VARIABILITY_FEASIBILITY.md` | Feasibility memo |
| `EXTERNAL_VARIABILITY_DETECTOR_PROTOCOL.md` | Detector mechanics |
| `external_variability_go_no_go.json` | Go/no-go record |
| `scripts/smoke_external_variability_detector.py` | Smoke tests |
| `tests/external/` | Unit tests (not evidence) |

---

## 14. Effort and risk (planning estimates)

| Item | Estimate |
|------|----------|
| Harness + pilot (Phase 1) | 3–5 days |
| Full sweep local models | 7–10 days |
| Optional commercial APIs | +2–3 days |
| Analysis + manuscript drafts | 3–5 days |
| **Total** | **3–4 weeks** |

**Main risk:** low `variable_rate` among valid completions → null descriptive result with limited reviewer impact.

**Expected review value:** **medium** (supports ecological discussion; does not replace trace-contract caveats).
