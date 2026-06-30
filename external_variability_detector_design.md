# External interface-agnostic variability detector — design spec (pre-freeze)

**Study ID:** `RQ-EXT-E`  
**Date:** 2026-06-30  
**Status:** Design only — **not implemented**; must be frozen before any external evaluation corpus is scored.

This document defines a **new detector generation**, separate from frozen INVERT Class E (`deterministic_randomized.py`, SHA256 `ab5e5a9175…`).

---

## 1. Problem statement

Frozen Class E measures **visit-trace identity** under the `ItemProcessor` / `visit_fn` harness. External smoke probes (`EXTERNAL_CLASS_E_FEASIBILITY.md`) showed abstention on arbitrary Python and EffiBench-X without that contract.

**RQ-EXT-E** asks a different question:

> On independent executable programming benchmarks not designed for INVERT, do functionally valid solutions exhibit inter-execution variability, and does that variability expose reproducibility behavior not captured by one-shot functional tests?

This is a **prevalence / audit** question, not pole recovery. No prompt names a randomized or deterministic target.

---

## 2. Design options evaluated

| Option | Mechanism | Pros | Cons | Verdict |
|--------|-----------|------|------|---------|
| **1. Output-stability** | Run solution *N* times on fixed inputs; hash serialized outputs | No INVERT API; no manual labels; mirrors “one-shot test misses run-to-run drift” | Sparse signal on canonical solutions; must handle float/set ordering | **Primary — freeze this** |
| **2. Execution-trace** | `sys.settrace` / line-event traces across *N* runs | Richer than stdout when outputs identical but paths differ | Environment noise; overhead; harder to defend externally | **Fallback only** if output-stability yield &lt; 5% on pilot LLM sample |
| **3. Runtime-variance** | Wall-clock distribution across *N* runs | Easy to measure | Confounds scheduling noise with code process | **Secondary descriptive metric only** — not a classification axis |

**Recommendation:** freeze **Option 1 (output-stability)** as the sole primary classifier.

---

## 3. Frozen detector: `external_output_stability` (proposed)

### 3.1 File placement (separation from Class E)

| Item | Class E (frozen, do not reuse) | RQ-EXT-E (new) |
|------|-------------------------------|----------------|
| Path | `src/invert_core/detectors/deterministic_randomized.py` | `src/invert_external/detectors/output_stability.py` *(new package)* |
| Contract | `ItemProcessor`, `visit_fn`, `expected_items` | None — stdin/stdout or callable entry via benchmark harness only |
| Classification | `deterministic` / `randomized` pole | `stable` / `variable` / `invalid` / `timeout` |
| Oracle | INVERT task JSON | Benchmark official tests (EvalPlus/HumanEval/MBPP) |

Keep `invert_external/` out of confirmatory Core v2 hashes. Record SHA256 at freeze time in `prereg/external_variability_protocol.json`.

### 3.2 Inputs

- `solution_source`: path to Python source or extracted completion.
- `harness_spec`: benchmark-provided test invocation (function name + argument tuples **or** stdin vector list).
- `run_count`: **10** (frozen default; Class E used 5 internally — external study uses 10 for flaky detection power).
- `timeout_sec`: **2.0** per run (frozen).
- `environment`: `PYTHONHASHSEED=0`, `TZ=UTC`, single-threaded subprocess (no `multiprocessing` pool in harness).

### 3.3 Execution protocol (frozen before scoring)

1. **Behavioral gate (single shot):** run benchmark official test suite once. If fail → label `invalid` (generation/functional failure); do not enter variability denominator.
2. **Repeatability sweep:** for each frozen input vector in `harness_spec.fixed_inputs` (minimum: all public/EvalPlus-visible inputs used in step 1):
   - Execute solution `run_count` times with identical inputs.
   - Serialize output: `json.dumps(result, sort_keys=True, default=repr)` for return values; SHA-256 of normalized stdout bytes for stdin tasks.
3. **Aggregate per solution:** collect set of unique output hashes across all inputs and runs.

### 3.4 Classification rules (frozen)

| Label | Rule |
|-------|------|
| `stable` | Exactly **1** unique output hash across all `run_count × len(fixed_inputs)` executions, and step 1 passed |
| `variable` | **≥ 2** unique output hashes, and **every** execution completes without exception within timeout |
| `invalid` | Behavioral gate fails, or any repeat run raises uncaught exception |
| `timeout` | Any repeat run exceeds `timeout_sec` |
| `ambiguous` | Mixed pass/fail across repeats with identical inputs (flaky) — report separately; excluded from stable/variable prevalence |

**No** mapping to INVERT poles `deterministic` / `randomized`. **No** post-hoc threshold tuning.

### 3.5 Explicit exclusions (frozen)

- Do not wrap code in `ItemProcessor`, `GraphTraversal`, or any `visit_fn` adapter.
- Do not filter tasks after seeing variability rates (task list frozen from HumanEval+ task IDs).
- Do not prompt models for randomness or determinism.
- Do not use runtime variance as primary label.

### 3.6 Secondary metrics (non-classifying)

Record but do not use for primary label:

- `wall_clock_cv` = coefficient of variation of wall time across runs.
- `trace_unique_count` (only if optional trace module enabled in pilot branch).

---

## 4. Validation plan before external scoring

| Control | Purpose |
|---------|---------|
| `synthetic_stable.py` | Pure function, no randomness → expect `stable` |
| `synthetic_variable.py` | `random.random()` in output → expect `variable` |
| `synthetic_flaky.py` | `random.choice` pass/fail → expect `ambiguous` |
| Frozen INVERT Class E artifacts | Run **new** detector only; expect most INVERT-valid artifacts `stable` on harness translation **without** ItemProcessor (likely `invalid` if naively translated — do not use INVERT tasks as external positives) |

Positive controls for the **new** detector use synthetic micro-benchmarks only, not Class E detector outputs.

---

## 5. Analysis outputs (descriptive only)

Report on **valid-only** solutions (after behavioral gate):

- `prevalence_stable`, `prevalence_variable`, `prevalence_flaky`
- Breakdown by generator model (if LLM-generated sample)
- Comparison: “one-shot pass” vs “variable despite pass” (addresses RQ-EXT-E directly)
- Optional: HumanEval vs HumanEval+ gate — count solutions that pass HumanEval once but show variability under augmented inputs

**Paper placement:** Threats / Limitations / appendix — **not** confirmatory Results alongside frozen Class E recovery rates.

---

## 6. Fallback: execution-trace module (not frozen unless pilot fails)

Trigger for reconsideration:

- Pilot on **≥ 50** LLM-generated HumanEval+ solutions with output-stability `stable` rate &gt; 98% **and** manual inspection shows hidden path diversity.

If triggered, add `invert_external/detectors/line_trace_stability.py` with:

- Frozen line-number trace (not bytecode offsets)
- Same `stable` / `variable` semantics on trace hashes
- Separate SHA256 and separate prevalence table

Do not combine with output-stability into a single tuned score.

---

## 7. Implementation checklist

- [ ] Create `prereg/external_variability_protocol.json` (inputs, N, timeout, serialization)
- [ ] Implement `output_stability.py` + unit tests on synthetic controls
- [ ] Compute and record detector SHA256
- [ ] Integrate EvalPlus/HumanEval harness (no INVERT task JSON)
- [ ] Run pilot: canonical HumanEval+ solutions (expect ~100% stable)
- [ ] Run evaluation: frozen generator sample (e.g., 3 Ollama models × 164 tasks × 1 completion)
- [ ] Export `results/external_variability/` CSVs
- [ ] Manuscript: one paragraph + appendix table (exploratory)

**Estimated implementation:** 4–6 days detector + harness; 7–10 days generation + analysis; **3–4 weeks** total with freeze discipline.
