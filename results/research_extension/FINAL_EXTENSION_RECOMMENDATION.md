# INVERT Research Extension — Final Recommendation

**Date:** 2026-06-30  
**Papers/datasets inspected:** 25 (`hypothesis_candidates.csv`)  
**Top hypotheses selected:** 10 (`top10_hypotheses.csv`)  
**Preflight folders:** `experiments/research_extension/H01_*` … `H10_*` (all `status: ready`)

---

## Top 10 hypotheses (ranked)

1. **H01** — Temperature increases bounded process trace diversity  
2. **H02** — Neutral prompts reveal model-specific process pole bias  
3. **H03** — Reasoning vs coder models differ in process traces  
4. **H04** — Self-consistency / pass@k selection collapses process diversity  
5. **H05** — Automated repair shifts process signatures  
6. **H06** — Code-specialized models more process-monoculture than base  
7. **H07** — Model size vs process diversity  
8. **H08** — Cross-class process coupling (frozen-data)  
9. **H09** — Repetition scaling reveals hidden diversity at T=0  
10. **H10** — Instruction tuning reduces process diversity  

---

## Top 2 recommended for execution

### 1. H01 — Temperature × process trace diversity

**Why it improves TOSEM acceptance**
- Converts INVERT from “we can recover poles at T=0” into an **empirical law** about sampling and process behavior.
- Directly follows Lee et al. 2025 / Hong et al. 2024 while using **execution traces**, not LLM-judge similarity.
- Responds to **perfect-score skepticism**: even if recovery stays 1.0, **richness/H vs T** is a non-trivial axis.
- Uses existing artifact pipeline; **no detector or frozen-run changes**.

**Real discovery?** Yes, if C/D show ΔH > 0 at T ≥ 0.8. Null result (monoculture everywhere except E randomized) is also publishable as strong monoculture evidence.

**Attacks:** methodological-only contribution ✓; perfect scores ✓; local models (exploratory framing) ✓.  
**Does not attack:** external validation (by design — internal discovery).

### 2. H02 — Neutral-prompt process bias

**Why it improves TOSEM acceptance**
- Addresses the **prompt-named pole** threat (Threats §Prompt sensitivity) with a direct empirical test.
- Produces a **software engineering finding**: models have **default process priors** under outcome equivalence.
- Independent of H01 — bias may exist even when diversity is low.

**Real discovery?** Yes, if models show stable, differing default poles (e.g., Devstral → eager, Qwen → BFS).

**Attacks:** synthetic separability ✓; methodological-only ✓; prompt sensitivity ✓.

**Risk:** task stubs may implicitly encode poles — mitigate with pilot on 4 tasks and explicit construct-validity paragraph.

---

## What to implement next

| Priority | Action | Est. effort |
|----------|--------|-------------|
| 1 | Run **H01** generation sweep (C/D/E × 3 models × 4 T × 20 reps) | 1–2 weeks |
| 2 | Run **H02** pilot (4 tasks × 3 models × 15 reps) | 3–5 days |
| 3 | Reuse `invert_discovery/ecology/` fingerprints on new detection CSVs | 1 day |
| 4 | If H01 null on C/D → **H09** rep scaling on one model | 1 week |

## What to abandon

- Full **Process Ecology Atlas** (preflight: `full_pea_recommended: false`)
- **External HumanEval+ variability** as main paper claim
- **SWE-bench / LiveCodeBench** primary studies
- **EffiBench** Class D external probe (adapter/co-design)
- **Verbalized Sampling** as core INVERT experiment
- **H08** as standalone section unless H01/H02 produce signal (frozen monoculture limits coupling)

## Second-paper risk

| Candidate | Risk |
|-----------|------|
| H01, H02 | Low — fit as Results subsection + Discussion |
| H05 repair drift | Medium — could grow into APR paper |
| H10 instruction monoculture | Medium — needs many model pairs |
| H18/EpiCoder-style training | High — separate ML paper |

---

## Artifact locations

```
results/research_extension/
  hypothesis_candidates.csv      # 25 sources
  HYPOTHESIS_SCAN_REPORT.md
  top10_hypotheses.csv
  TOP10_EXTENSION_PLAN.md
  FINAL_EXTENSION_RECOMMENDATION.md
  H01_temperature_process_diversity/preflight_result.json
  ... (H02–H10 preflight_result.json)

experiments/research_extension/
  H01_temperature_process_diversity/  # README, config.yaml, schema.csv, go_no_go.json, run_preflight.py
  ...
```

**Paper:** not modified (`~/papers/invert/paper` untouched).
