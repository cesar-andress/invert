# Top-10 Extension Plan — INVERT Empirical Research

**Goal:** Strengthen ACM TOSEM contribution from controlled methodology toward **empirical software engineering discoveries** about LLM-generated code process behavior.

**Constraints (inviolable):** no frozen detector changes; no frozen run edits; no human annotation; no LLM judges; no external adapters; no paper edits yet.

---

## Ranking summary

| Rank | ID | Hypothesis (short) | Impact | Novelty | Effort | Rejection ↓ |
|------|-----|-------------------|--------|---------|--------|-------------|
| 1 | H01 | Temperature → process diversity | ★★★★★ | ★★★★☆ | M | ★★★★☆ |
| 2 | H02 | Neutral-prompt process bias | ★★★★★ | ★★★★★ | M | ★★★★★ |
| 3 | H03 | Reasoning vs coder process | ★★★★☆ | ★★★★★ | M | ★★★★☆ |
| 4 | H04 | Self-consistency diversity collapse | ★★★★☆ | ★★★★☆ | M | ★★★☆☆ |
| 5 | H05 | Repair process drift | ★★★★☆ | ★★★★★ | H | ★★★☆☆ |
| 6 | H06 | Specialized vs base monoculture | ★★★☆☆ | ★★★☆☆ | M | ★★★☆☆ |
| 7 | H07 | Model size vs diversity | ★★★☆☆ | ★★★☆☆ | L–M | ★★☆☆☆ |
| 8 | H08 | Cross-class process coupling | ★★★☆☆ | ★★★☆☆ | L | ★★☆☆☆ |
| 9 | H09 | Rep scaling at T=0 | ★★★☆☆ | ★★★☆☆ | M | ★★☆☆☆ |
| 10 | H10 | Instruction monoculture | ★★★☆☆ | ★★★☆☆ | H | ★★★☆☆ |

---

## H01 — Temperature and process trace diversity

**RQ:** Does increasing sampling temperature increase bounded process-trace diversity among valid, outcome-equivalent artifacts on Classes C, D, and E?

**Motivation:** Lee et al. 2025; Hong et al. 2024; INVERT preflight monoculture at T=0.

**Design:**
- Tasks: existing Family1 JSON for eager/lazy, bfs/dfs, deterministic/randomized (3 tasks each).
- Models: `qwen2.5-coder:14b`, `devstral:latest`, `qwen3-coder:30b`.
- Temperatures: `{0.0, 0.4, 0.8, 1.0}`.
- Reps: 20 per (model, task, pole, T).
- Prompts: **existing named-pole** JSON prompts (unchanged semantics).
- Pipeline: standard `invert-core` generate → behavioral validate → frozen detect → fingerprint from CSV trace columns.
- Metrics: richness, Shannon H, Simpson, valid_rate, recovery_rate, diversity vs T curves.

**Positive claim:** Process diversity rises with T on ≥2 dynamic classes while behavioral validity remains acceptable.

**Null claim:** Monoculture persists on C/D at all T; only E randomized diversifies — generative process homogeneity under equivalence.

**Go/no-go:** ≥2 dynamic classes show ΔH ≥ 0.5 bits from T=0 to T=0.8 for ≥2 models with valid_rate ≥ 0.5.

**Risks:** Diversity only on randomized pole; validity collapse at high T.

---

## H02 — Neutral-prompt process bias

**RQ:** When prompts omit explicit pole names, do models default to stable, model-specific process poles detectable by frozen INVERT detectors?

**Motivation:** Kirk 2024 monoculture; INVERT threat “prompt-named poles”; tests whether process is prompt-driven or model-prior-driven.

**Design:**
- Neutral prompt template: specify I/O contract and stub only; **do not** name eager/lazy/BFS/DFS/deterministic/randomized.
- Same tasks/models as H01 subset; T=0; 15 reps.
- Metrics: distribution over `detected_method`, entropy of pole assignments, per-model default pole rate.

**Positive claim:** Models exhibit reproducible default process strategies (e.g., always eager, always BFS) differing across families.

**Null claim:** Uniform pole distribution or validity collapse — neutral prompts insufficiently specified.

**Go/no-go:** ≥2 models show ≥70% mass on one detected pole for ≥2 classes with valid_rate ≥ 0.4.

**Risks:** Task JSON stubs may implicitly encode pole; construct validity threat — document and pilot 3 tasks first.

---

## H03 — Reasoning vs coder process strategies

**RQ:** At matched functional validity, do reasoning models produce different bounded process traces than coder models?

**Motivation:** o1 2024; o1-Coder 2024.

**Design:** Pair `qwen2.5-coder:14b` with `deepseek-r1` or `qwen3` thinking variant if available in Ollama; named poles; T=0; 10 reps; fingerprint divergence + recovery.

**Go/no-go:** Significant fingerprint distance on ≥2 classes with matched valid_n ≥ 30.

**Risks:** API-only reasoning models; size confound.

---

## H04 — Self-consistency process collapse

**RQ:** Does selecting one valid sample from k candidates reduce process diversity?

**Motivation:** Hong 2024 — high pass@k, high similarity.

**Design:** k=20 at T=0.8; measure H on all valid vs H on first-valid / majority-output-selected artifact.

**Go/no-go:** median diversity_loss ≥ 0.3 bits on ≥2 classes.

---

## H05 — Repair process drift

**RQ:** When invalid artifacts are repaired to pass behavioral gates, are process poles preserved?

**Motivation:** Trace-based APR 2025; DynaFix 2025.

**Design:** Collect invalid from pilots; single-pass automated repair (model or template); re-run frozen detectors; pole_flip_rate.

**Go/no-go:** ≥15% repaired-valid flip pole or fingerprint vs intent.

**Risks:** Low repair success rate; repair is new generation.

---

## H06–H10 (abbreviated)

See `top10_hypotheses.csv` and per-folder `README.md`.

---

## Recommended first execution: H01 + H02

### Why these two

| Criticism | H01 | H02 |
|-----------|-----|-----|
| Methodological-only contribution | Adds empirical law (T vs process H) | Adds empirical law (default process priors) |
| Perfect-score / synthetic separability | Shows diversity regime beyond recovery=1 | Shows behavior **without** named pole in prompt |
| Prompt-named poles threat | Holds poles fixed; isolates sampling | Directly tests pole removal |
| Local-only models | Same Ollama stack; publishable as exploratory | Same |
| Lack of external validation | Does not fake external validation; adds **internal discovery** axis | Same |
| Monoculture preflight | Natural follow-up — preflight motivated this | Independent axis — bias may exist even when diversity low |

### Real empirical discovery?

- **H01:** Yes if C/D diversify at T>0 — falsifies “frozen runs exhaust LLM process behavior.”
- **H02:** Yes if default poles differ by model — new SE fact about codegen process priors under equivalence.

### Second-paper risk

- **H01, H02:** Strengthening section / secondary contribution — **not** a second paper if scoped to Family1.
- **H05, H10:** Higher risk of sprawling into separate APR/training paper if expanded.

### Abandon

- Full PEA atlas (preflight no-go)
- External HumanEval variability as main claim
- SWE-bench / LiveCodeBench primary studies
- Verbalized Sampling as core experiment

---

## Implementation order

1. Execute **H01** temperature sweep (Classes C, D, E) — ~1–2 weeks generation + analysis.
2. Execute **H02** neutral prompt pilot (3 tasks × 2 classes) before full sweep.
3. If H01 null on C/D: run **H09** rep scaling on best model only.
4. If H02 go: add **H03** reasoning comparison.
5. Defer **H05** until invalid artifact pool characterized.

---

## Output layout

```
results/research_extension/
  hypothesis_candidates.csv
  top10_hypotheses.csv
  HYPOTHESIS_SCAN_REPORT.md
  TOP10_EXTENSION_PLAN.md
  H01_temperature_process_diversity/   # after execution
  H02_neutral_prompt_process_bias/

experiments/research_extension/
  H01_temperature_process_diversity/
  ...
```
