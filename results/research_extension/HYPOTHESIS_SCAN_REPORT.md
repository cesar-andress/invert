# Hypothesis Scan Report — INVERT Research Extension

**Date:** 2026-06-30  
**Scope:** Literature and open-data scan (2023–2026) for process-level hypotheses testable with INVERT Core v2 **without** modifying frozen detectors, frozen runs, human annotation, LLM judges, or external interface adapters.

**Sources inspected:** 25 candidate papers/datasets (see `hypothesis_candidates.csv`).

---

## Executive summary

Recent code-LM literature converges on a gap INVERT is positioned to fill: **functional correctness metrics hide implementation and process homogeneity**. Papers measure algorithmic or semantic similarity (often with LLM judges); INVERT can measure **bounded execution-process fingerprints** under **outcome equivalence** with frozen rule-based detectors.

The internal **process trace diversity preflight** (2026-06-30) establishes a critical baseline: at **temperature 0** on frozen generalization runs, Classes **C** and **D** are trace-monocultures among valid, correctly recovered artifacts; diversity appears only on **Class E / randomized pole** (semantics-aligned, not hidden biodiversity).

Therefore the highest-ROI extensions are **interventions that literature already links to diversity** (temperature, neutral prompts, multi-sample selection, repair) measured with **INVERT process traces**, not another benchmark family or adapter-based external validation.

---

## Literature themes mapped to INVERT

### 1. Implementation / algorithmic diversity collapse

| Source | Claim | INVERT angle |
|--------|-------|--------------|
| Lee et al. 2025 (EMNLP Findings) | Low algorithmic diversity vs humans; temperature ↑ diversity | Replicate at **process-trace** level on Family1 C/D/E |
| Hong et al. 2024 | Correct code is often similar code; instruction tuning ↑ pass ↓ diversity | Use fingerprint richness instead of LLM Sim@K |
| Kirk et al. 2024 | Generative monoculture from alignment | Neutral-prompt default pole bias test |
| Zhang et al. 2025 (Verbalized Sampling) | Mode collapse; distribution prompts help | Lower priority — prompt hack, high construct risk on Family1 |

### 2. Temperature and multi-sample inference

| Source | Claim | INVERT angle |
|--------|-------|--------------|
| TURN 2025 | Optimal T higher for pass@k than pass@1 | Joint curves: valid_rate, recovery, process H vs T |
| pass@k scaling (Smith 2025) | T* scales with k | Secondary analysis on H01 data |
| Chen/Austin HumanEval/MBPP | pass@k standard | Contrast only — not extension target |

### 3. Reasoning models and code

| Source | Claim | INVERT angle |
|--------|-------|--------------|
| OpenAI o1 2024 | Extended CoT improves hard code | Reasoning vs coder trace comparison |
| o1-Coder 2024 | Think-then-code improves IOI-style tasks | Same, on Family1 quantity/order/variability |
| P-GRPO 2025 | Process rewards matter in RL | Motivation only — training out of scope |

### 4. Repair and execution traces

| Source | Claim | INVERT angle |
|--------|-------|--------------|
| Trace-based APR (KnowledgeNLP 2025) | Traces help repair selectively | **Repair process drift**: does fix preserve pole? |
| DynaFix 2025 | Iterative trace feedback | Simplified one-pass variant on INVERT invalid artifacts |
| SWE-bench 2023 | Real-repo repair | Too heavy; defer |

### 5. Execution-based evaluation

| Source | Claim | INVERT angle |
|--------|-------|--------------|
| EvalPlus 2023 | Augmented tests expose fragility | Already probed externally — not primary path |
| LiveCodeBench 2024 | Anti-contamination eval | Excluded (new benchmark family) |
| EffiBench 2024 | Efficiency stereotypes | Adapter/co-design risk — deprioritize |

### 6. Internal INVERT evidence

| Source | Finding | Implication |
|--------|---------|-------------|
| Process trace preflight | C/D monoculture at T=0 | Temperature / neutral-prompt studies justified |
| External variability pilot | 0% output instability on HumanEval+ valid | Output-only external metric weak; process-internal stronger |
| Frozen generalization | ~100% recovery | Skeptics will cite co-design; need **non-recovery** empirical axes |

---

## Testability filter (applied)

**Included** if: uses Family1 tasks + existing detectors + behavioral oracles; metrics from emitted traces; open reproducible pipeline.

**Excluded** if: requires HumanEval/MBPP as primary corpus; needs LLM clustering/judge; needs GraphTraversal/ItemProcessor adapters on external code; human labels; detector retuning.

---

## Candidates deprioritized or abandoned

| ID | Reason |
|----|--------|
| C04 Verbalized Sampling | Prompt trick; weak tie to INVERT poles |
| C06–C07, C14, C24 | External benchmark families |
| C13 EffiBench | External adapter / co-design risk |
| C15 SWE-bench | Effort >> 8 weeks for fair process audit |
| C18 EpiCoder | Training/data synthesis — second paper |
| C23 P-GRPO | RL training — not artifact extension |
| PEA full atlas | Preflight `full_pea_recommended: false` |

---

## Top hypothesis families (pre-ranking insight)

1. **Sampling interventions** (temperature, N reps, self-consistency) — literature-backed, no detector change.
2. **Prompt neutrality** (process bias) — attacks prompt-named-pole threat directly.
3. **Model family contrasts** (reasoning, specialized, size) — moderate cost, confound risks.
4. **Repair drift** — novel SE claim, higher implementation cost.
5. **Frozen-only coupling** (H08) — cheap but weak after monoculture preflight.

---

## Artifact compatibility

All top-10 designs:
- Add new runs under `results/research_extension/<Hxx>/`
- Reuse `invert_core` generation + evaluation CLI patterns
- Read trace fingerprints from **existing detector CSV columns** (`trace`, `visit_trace`, `traces`, etc.)
- Do **not** modify `src/invert_core/detectors/` or frozen run exports

---

## Next step

See `TOP10_EXTENSION_PLAN.md` and `experiments/research_extension/H01_*` … `H10_*` for preregistered designs and preflight stubs.

**Recommended first execution:** H01 (temperature) + H02 (neutral prompt bias).
