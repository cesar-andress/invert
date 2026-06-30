# External Interface-Agnostic Variability Study — Feasibility Plan

**Study ID:** RQ-EXT-E  
**Date:** 2026-06-30  
**Repositories:** artifact `~/papers/invert/invert` · manuscript `~/papers/invert/paper`  
**Relation to prior work:** supersedes the *frozen Class E detector* external smoke (`EXTERNAL_CLASS_E_FEASIBILITY.md`, `no-go`). This plan designs a **new** detector generation.

---

## Executive summary

| Question | Answer |
|----------|--------|
| Is an external variability study **feasible**? | **Yes**, with a new output-stability detector and HumanEval+ harness |
| Does it **avoid trace-contract dependence**? | **Yes** — no `ItemProcessor`, `GraphTraversal`, or `visit_fn` |
| Does it **validate frozen Class E recovery**? | **No** — different RQ, different detector, descriptive prevalence only |
| **Materially improve TOSEM chances**? | **Medium** — addresses ecological-validity criticism if framed as exploratory; will not convert synthetic benchmark skeptics alone |
| **Proceed now (full study before submission)?** | **No** — `revise-plan`: run 3-day pilot, then 4-week full study for revision |
| **Proceed with pilot?** | **Yes** |

**Machine-readable decision:** `external_variability_go_no_go.json`

---

## 1. Research question

**RQ-EXT-E:** On independent executable programming benchmarks not designed for INVERT, do functionally valid generated solutions exhibit inter-execution variability, and does that variability expose reproducibility behavior not captured by one-shot functional tests?

### Distinction from Class E (mandatory)

| | Frozen Class E | RQ-EXT-E |
|---|----------------|----------|
| Detector | `deterministic_randomized.py` | `output_stability.py` (proposed, new package) |
| API | `ItemProcessor` + `visit_fn` | Benchmark harness only |
| Unit of analysis | Visit-trace identity under harness | Output hash identity across repeated runs |
| Prompt | Names deterministic vs randomized pole | **No** randomness/determinism in prompt |
| Claim type | Pole recovery on valid artifacts | Prevalence of run-to-run output instability |
| Paper tier | Confirmatory (frozen Core v2) | Exploratory (Threats / appendix) |

Prior probe conclusion (`external_class_e_go_no_go.json`): repeated execution **without** a new extraction layer does not escape the INVERT contract. RQ-EXT-E implements that new layer as **output-stability**, not an adapter.

---

## 2. Candidate datasets

Full matrix: `external_variability_dataset_options.csv`

### Summary ranking

| Rank | Dataset | Verdict |
|------|---------|---------|
| **1** | **HumanEval+ (EvalPlus)** | Primary — best ROI |
| 2 | HumanEval (base) | Secondary — smaller test surface |
| 3 | MBPP sanitized (377) | Replication / scale-up after pilot |
| 4 | MBPP full | Optional extension |
| **5** | EffiBench-X Python | **Deprioritize** — Docker/stdin friction; prior D/E probes failed |
| — | INVERT Family 1 | **Exclude** — internal trace-contract benchmark |

### HumanEval+ (recommended)

- **Open:** OpenAI HumanEval + open-source EvalPlus (`evalplus` on PyPI); already cited in manuscript (`liu2023evalplus`).
- **Python:** native function-call evaluation model.
- **Tests:** augmented suite (~80× more tests than HumanEval) — directly supports “one-shot pass misses instability.”
- **Repeated execution:** run same function on frozen input tuples in subprocess; feasible.
- **Canonical solutions:** included; expect ~100% `stable` on reference (sanity baseline).
- **Output capture:** return-value JSON serialization + hash.
- **Determinism:** high for references; variability signal expected on **LLM-generated** completions that pass once.
- **Multiple valid outputs:** rare; EvalPlus contract treats test failure as failure.
- **Setup effort:** 3–4 days (harness + EvalPlus integration).

### MBPP

- Larger corpus, similar execution model.
- Slightly noisier task specs; use after HumanEval+ pilot confirms non-trivial variability prevalence.

### EffiBench-X

- Local HF dataset load already verified (`EXTERNAL_EFFIBENCH_FEASIBILITY.md`).
- Stdin/stdout + Docker evaluate pipeline; Class E smoke: `exec_failed` on native solutions.
- Efficiency benchmark, not reproducibility-audit benchmark.
- **5–8 days** extra sandbox work for uncertain payoff on RQ-EXT-E.

---

## 3. Detector recommendation

**Freeze: output-stability detector (Option 1).**

Specification: `external_variability_detector_design.md`

### Why output-stability

- Clean operationalization of “one-shot functional test is insufficient.”
- No manual annotation.
- No INVERT API or code adaptation.
- Aligns with strict rules (no pole-named prompts, freeze before evaluation).

### Why not execution-trace (primary)

- `sys.settrace` noise, version dependence, and reviewer skepticism on trace equivalence.
- Reserve as **fallback** only if pilot shows &lt; 2% variable rate on LLM sample but qualitative path diversity exists.

### Why not runtime-variance (primary)

- Confounds OS scheduling with code-level process; weak construct validity for RQ-EXT-E.

---

## 4. Strict rules compliance

| Rule | Compliance |
|------|------------|
| No prompt requesting randomness/determinism | Use standard HumanEval+ completion prompts only |
| No manual labeling | Hashes + frozen rules → `stable` / `variable` / `invalid` / `timeout` |
| No adapting code into INVERT APIs | Harness calls benchmark entry points directly |
| No post-hoc tuning | Task list, N=10, timeout, serialization frozen in `prereg/external_variability_protocol.json` before scoring |
| Freeze detector before evaluation | SHA256 recorded; separate from Class E hash |
| No frozen-run modification | New results under `results/external_variability/` only |

---

## 5. Study phases

### Phase 0 — Freeze (days 1–2)

- Write `prereg/external_variability_protocol.json`.
- Implement `invert_external/detectors/output_stability.py` + synthetic unit tests.
- Record detector SHA256; **no** external corpus scoring yet.

### Phase 1 — Pilot (days 3–5) — **go**

- **A.** HumanEval+ canonical solutions (N=164): expect ≥ 99% `stable` (environment sanity).
- **B.** Small LLM sample: 1 model × 30 stratified tasks × 1 completion (reuse Ollama stack).
- **Decision gate:** if variable prevalence among valid completions ≥ 2%, proceed to Phase 2; else report null result in appendix (still valuable for threats).

### Phase 2 — Full external sweep (days 6–21) — post-pilot

- 3 local models × 164 HumanEval+ tasks × 1 completion (or match existing Ollama inventory).
- Behavioral gate: EvalPlus pass@1 equivalent.
- Variability sweep: 10 runs × frozen inputs.
- Export CSV: `results/external_variability/humaneval_plus_prevalence.csv`.

### Phase 3 — Manuscript (days 22–28)

- One paragraph in Threats / Limitations: exploratory RQ-EXT-E, separate detector.
- Appendix table: prevalence counts; **no** merge into Class E recovery tables.
- Optional: “passes once but variable on repeat” count.

---

## 6. Expected outcomes and interpretation

### Best case (medium–high review value)

- Non-trivial fraction (e.g., 5–15%) of **valid** LLM solutions are `variable` under output-stability.
- Some solutions pass HumanEval once but fail consistency under repeat or EvalPlus-augmented inputs.
- Supports manuscript claim: functional validation alone under-specifies reproducibility; INVERT’s variability **theme** has external face validity without claiming Class E transfer.

### Null case (still publishable)

- &lt; 1% variable among valid completions on HumanEval+.
- Report honestly; strengthens “variability pole is rare in the wild” limitation.
- Review value: **low–medium** — shows due diligence, does not defeat trace-contract criticism.

### Failure modes to avoid

- Presenting RQ-EXT-E as confirmatory Class E validation.
- Tuning N or hash serialization after seeing prevalence.
- Wrapping external solutions in INVERT harnesses.
- Adding EffiBench-X before HumanEval+ pilot completes.

---

## 7. Effort and resources

| Component | Days |
|-----------|------|
| Detector + prereg freeze | 2 |
| EvalPlus/HumanEval harness | 2–3 |
| Pilot (canon + 30-task LLM) | 2–3 |
| Full generation + sweep | 10–14 |
| Analysis + manuscript text | 3–5 |
| **Total** | **~21–28 days (4 weeks)** |

**Pilot-only (pre-submission):** 3–5 days.

Reuse existing: Ollama generation infra, subprocess isolation patterns from behavioral oracles, abstention reporting style.

**New dependencies (verify licenses):** `evalplus` package; `datasets` for HumanEval if not bundled in evalplus.

---

## 8. TOSEM review-risk mapping

| Reviewer attack | How RQ-EXT-E helps | Limit |
|-----------------|-------------------|-------|
| “Evidence is only synthetic trace-contract tasks” | Shows independent benchmark audit for **reproducibility**, not pole recovery | Does not prove quantity/order axes |
| “Class E is co-designed” | New detector with no INVERT API | Different measurement; not a replication |
| “One-shot pass@k is enough” | Directly tests repeat-run instability | Null result weakens narrative |
| “Where is external validation?” | Documented exploratory study with frozen protocol | Must not overclaim |

**Expected review value:** **medium** (high only if variable prevalence is materially non-zero and HumanEval-vs-HumanEval+ gap is demonstrated).

---

## 9. Deliverables (this planning pass)

| File | Purpose |
|------|---------|
| `EXTERNAL_VARIABILITY_FEASIBILITY.md` | This document |
| `external_variability_dataset_options.csv` | Dataset comparison matrix |
| `external_variability_detector_design.md` | Frozen detector spec |
| `external_variability_go_no_go.json` | Machine-readable decision |

### Not in scope of this pass

- Detector implementation
- LLM generation runs
- Manuscript Results edits
- Modifications to frozen Class E detector or Core v2 runs

---

## 10. Recommendation

**Feasibility:** **GO** for study design and pilot.  
**Full study before current submission:** **NO** (`revise-plan`).  
**Proceed:**

1. Implement and freeze `output_stability` detector (Phase 0).
2. Run 3–5 day HumanEval+ pilot (Phase 1).
3. If prevalence gate met, schedule 4-week full sweep for **revision round**, appendix-only reporting.
4. Keep frozen Class E evidence and RQ-EXT-E evidence **strictly separated** in text and artifacts.

---

## References within repository

- `EXTERNAL_CLASS_E_FEASIBILITY.md` — frozen Class E external `no-go`
- `EXTERNAL_EFFIBENCH_FEASIBILITY.md` — EffiBench Class D `revise-plan`
- `EXTERNAL_VALIDATION_CLOSURE.md` — confirmatory external validation out of scope for v1.0.1 submission
- `paper/threats_to_validity.tex` — trace-contract dependence framing
- `paper/REVIEW_LIMITATIONS.md` §16 — optional external sanity check (narrower than RQ-EXT-E)
