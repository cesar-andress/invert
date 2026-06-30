# H02 Redesign — Process Compliance Study (Preregistration Draft)

**Status:** Design evaluation only — **no implementation** until approved.  
**Replaces:** Neutral-prompt default-pole study (`H02_neutral_prompt_process_bias`).  
**Study ID:** `H02_process_compliance_pilot` (pilot) → `H02_process_compliance` (full, if GO)

---

## 1. Critical evaluation vs original neutral-prompt H02

### Original H02 (abandoned design)

| Aspect | Neutral-prompt design |
|--------|----------------------|
| Question | Do models have a **default pole** when the pole is unnamed? |
| Intervention | Single binary (named vs neutral) |
| Primary output | Pole distribution at one prompt condition |
| Contribution type | Descriptive bias snapshot |
| Failure mode | Task stubs/APIs may **imply** process; “neutral” is ill-defined; one cell per model; hard to connect to paper confirmatory runs |

### Redesigned H02 (process compliance)

| Aspect | Compliance design |
|--------|-------------------|
| Question | How **controllable** are process decisions under varying prompt specificity? |
| Intervention | **Three preregistered prompt levels** (dose of process information) |
| Primary metric | **Process Compliance Rate (PCR)** = P(recover requested pole \| valid artifact) |
| Contribution type | **Dose–response** characterization of process controllability |
| Strength | Turns prompt sensitivity from a **threat** into a **measured empirical axis**; comparable across models, classes, and poles |

### Verdict: scientifically stronger?

**Yes — materially stronger**, for five reasons:

1. **Construct validity:** “Compliance” is defined relative to a **preregistered requested pole** and **frozen detector outcome**, not an inferred default. The measuring instrument (INVERT detectors + behavioral gate) is explicit; the object of study is **model controllability**.

2. **Operationalizable gradient:** L1→L2→L3 is a **monotone specificity ladder**. Even null results (flat compliance across levels) are informative (“models ignore soft steering”). A single neutral prompt cannot distinguish “no default” from “invalid code” from “API-implied process.”

3. **Literature gap:** Lee/Hong/EvalPlus study **correctness and syntactic/algorithmic diversity**, not **compliance with named process constraints under outcome equivalence**. This is a defensible “first characterization” claim **within the Family1 harness contract** (scope honesty required).

4. **Synergy with H01 null:** H01 showed **temperature does not unlock process diversity** on C/D. H02 asks whether **prompt specificity** is the actual control lever — complementary, not redundant.

5. **Paper integration:** Confirmatory frozen runs become the **L3 anchor** (see §4), not a separate validation exercise.

### Residual weaknesses (must preregister mitigations)

| Risk | Mitigation |
|------|------------|
| L1 under-specified → validity collapse | Report **valid rate** and **PCR** separately; PCR only on valid artifacts; preregister minimum valid_n per cell |
| Task API implies process (visit_fn, lazy getters) | Document as **construct limit**; L1 measures compliance **under fixed harness**, not wild code |
| L2 (“efficient, readable”) inert | Accept as finding; do not replace wording post hoc |
| L3 wording drift vs frozen runs | **L3 MUST use verbatim Core v2 prompt blocks** (Method label + Operational requirement) — see §4 |
| Looks like prompt-engineering paper | Frame as **empirical SE**: controllability of non-functional process requirements under behavioral equivalence |

---

## 2. Does this attack “the requested pole is injected by the prompt”?

### What the criticism claims

Reviewers argue: high recovery may be **tautological** because prompts **name** the pole and include **operational instructions** co-designed with detectors (Threats §Prompt sensitivity; §Co-design).

### What compliance study does **not** claim

- It does **not** deny that L3 prompts name poles.  
- It does **not** replace confirmatory frozen results.  
- It does **not** assert ecological validity on arbitrary code.

### What it **does** do (reframing)

| Reviewer concern | Compliance response |
|------------------|---------------------|
| “Pole is in the prompt” | **Quantifies how much prompt specificity is required** for PCR to rise; separates L1/L2 from L3 |
| “Recovery is engineered” | Shows whether **weaker prompts still steer** the same pole among **valid** artifacts |
| “Only tests prompt following” | Measures **process** compliance via **execution traces**, not keyword matching |
| “Descriptive at one setting” | **Curves** across models and poles with **compliance gain** Δ(L3−L1) |

### Direct answer

**Partially transforms, partially concedes.**

- **Concedes:** At L3, the study **intentionally** matches the paper’s explicit-process condition — confirmatory runs remain the high-specificity endpoint.  
- **Transforms:** The criticism “you only recover because you named the pole” becomes testable:  
  - If PCR(L1) ≈ PCR(L3): prompt naming was **not necessary** (surprising; strong finding).  
  - If PCR(L1) ≪ PCR(L3): process compliance is **prompt-dependent** — report **compliance gain** and **pole difficulty** (which poles need L3).  
  - Either outcome is **empirical**, not defensive prose.

**Important:** This does **not** remove co-design or trace-contract limits. It **contextualizes** prompt dependence with data — which is what TOSEM reviewers ask for when they say “prompt sensitivity was not varied.”

---

## 3. Stronger redesign proposal (recommended before implementation)

The user’s three-level structure is sound. **One critical strengthening** and **one optional extension**:

### 3A. Anchor L3 to frozen Core v2 prompts (required)

Do **not** use minimal one-liners (“Use BFS”) alone as L3.

**Preregister L3 = existing Core v2 generation prompt** for each class:
- Shared header (code-only, stdlib, API block) — **identical across levels where present**
- **L3 adds:** `Method label:` + `Operational requirement:` blocks from `*_prompts.py` (current frozen protocol)

**L1 removes:** Method label + Operational requirement (+ L2 engineering line).  
**L2 adds only:** *“Implement an efficient, readable solution.”* (exact string, all tasks).

**Benefit:**  
- Frozen generalization CSVs become **retrospective L3 baseline** — **no regeneration for L3** in calibration pass.  
- Pilot/full study only **generates L1 and L2** (+ verify L3 matches frozen on subset).  
- Cuts cost ~33%; links compliance curves to **existing confirmatory numbers**.

### 3B. Process Compliance Frontier (PCF) — secondary preregistered scalar

For each (model, class, pole):

**PCF(τ)** = minimum prompt level ℓ ∈ {1,2,3} such that PCR ≥ τ  
Preregister τ = 0.95.

Summarizes “how hard is this pole to steer?” in one integer — excellent for paper Table/Figure.

### 3C. Optional: even stronger extension (defer unless pilot GO)

**Cross-class compliance coupling:** correlate PCF across C/D/E per model (extends abandoned H08 with clear metric). **Not required for pilot.**

### 3D. Do **not** add (reject)

- Neutral-only arm without requested-pole factorial design  
- Per-model prompt tuning  
- LLM judge for compliance  
- External HumanEval adapter  
- Temperature sweep (H01 closed)

---

## 4. Preregistered experimental design

### RQ-H02

**How does prompt specificity influence compliance with requested process constraints?**  
**Can different LLMs be reliably steered toward a requested process pole** among behaviorally valid artifacts?

### Factors (fixed)

| Factor | Levels |
|--------|--------|
| Prompt level | L1 minimal, L2 engineering, L3 explicit (Core v2 verbatim) |
| Class | C (quantity), D (order), E (variability) |
| Requested pole | Both poles per class (eager/lazy, bfs/dfs, deterministic/randomized) |
| Model | 2 strongest local coders: `qwen2.5-coder:14b`, `qwen3-coder:30b` |
| Temperature | 0.0 (fixed) |
| Reps | 10 per cell (pilot); 15 if full study |

### Tasks (pilot — do not change benchmark JSON)

| Class | Tasks (1–2) |
|-------|-------------|
| C | `mixed_signed_vector`, `small_positive_vector` |
| D | `branching_1`, `linear_chain` |
| E | `letters_8`, `numbers_10` |

### Prompt templates (frozen strings in `prompts.yaml`)

**Shared body (all levels):** Task ID, inputs, required class/API from existing `*_prompts.py` — **unchanged**.

**L1 suffix:** none (only “Implement a solution for the following problem.” inserted once at top).

**L2 suffix:** + `Implement an efficient, readable solution.`

**L3 suffix:** + full `Method label` + `Operational requirement` from Core v2.

**Requested pole** is still assigned per generation cell (factorial); prompts do not cross wires poles.

### Per-artifact fields

`model`, `prompt_level`, `class_id`, `task_id`, `requested_pole`, `detected_pole`, `behaviorally_valid`, `detector_recovery`, `abstention` (ambiguous), `strip_level` (raw only for pilot)

### Main metric

**PCR** = (# valid ∧ recovered requested pole) / (# valid)

Per: model × prompt_level × class × pole × task

### Secondary metrics

- L1 detected-pole distribution (valid artifacts)  
- Compliance gain: PCR(L3) − PCR(L1), PCR(L2) − PCR(L1)  
- Pole asymmetry: |PCR(pole_a) − PCR(pole_b)| at each level  
- Cross-model variance of PCR at each level  
- PCF(0.95) per model×class×pole  
- Valid rate (separate from PCR)

### Figures (preregistered)

1. **Compliance curves:** x = prompt level (1–3), y = PCR, facets = model × class  
2. **Heatmap:** model × class, color = PCR(L3) or mean PCR  
3. **L1 pole distribution:** stacked bar of detected_pole at L1 (valid only)

### Go / no-go (pilot)

**GO** if any:

1. Models differ in compliance curves (bootstrap CI on PCR non-overlapping at L1 or L2 for same class)  
2. Pole asymmetry: max_pole |PCR(L3)−PCR(L1)| ≥ 0.25 for some class  
3. Saturation differs: one model reaches PCR≥0.95 at L2, another requires L3

**NO-GO** if: flat curves, all PCR≈1 at L1, or validity collapse at L1 with no interpretable compliance signal.

### Independence constraints

- Module: `invert_discovery/process_compliance/`  
- Data: `data/discovery/h02_process_compliance/`  
- Results: `results/research_extension/H02_process_compliance/`  
- **No** edits to Core v2 detectors, frozen runs, task JSON, or paper

---

## 5. Expected contribution (paper framing)

> **Not:** “INVERT validates external benchmarks.”  
> **Yes:** “First empirical characterization of **process compliance** in LLM-generated code under **controlled behavioral equivalence**, measured via bounded execution traces.”

Position as **empirical SE discovery** enabled by INVERT instrumentation — same framing as redesigned extension plan.

---

## 6. Implementation gate

| Step | Action |
|------|--------|
| 0 | **This document approved** |
| 1 | Freeze `prompts.yaml` + `PREREGISTRATION.json` (SHA256) |
| 2 | Implement `invert_discovery/process_compliance/` |
| 3 | **Calibration:** verify L3 PCR matches frozen CSV aggregates (read-only) |
| 4 | Run **pilot** (L1+L2 generation only if L3 from frozen) |
| 5 | `H02_PILOT_REPORT.md` + GO/NO-GO |

**Do not implement** until Step 0 explicit approval.

---

## 7. Recommendation summary

| Question | Answer |
|----------|--------|
| Stronger than neutral H02? | **Yes** |
| Attacks prompt-injection criticism? | **Reframes with dose–response data**; does not eliminate co-design limit |
| Even stronger design? | **Anchor L3 to Core v2 verbatim + PCF(0.95) + optional L3 from frozen CSVs** |
| Proceed to implementation? | **After approval of this prereg** |
