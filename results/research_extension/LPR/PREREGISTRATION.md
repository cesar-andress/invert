# Latent Process Risk (LPR): Preregistration

**Study identifier:** `LPR-2026-001`  
**Registration platform:** Open Science Framework (OSF) — *to be deposited before any primary analysis*  
**Status:** Preregistered design only. No code, data, or results exist at registration time.  
**Version:** 1.0  
**Date:** 2026-06-29  
**Authors:** *[to be completed before OSF deposit]*

---

## Study summary

**Title:** Latent Process Risk: Predictive Information in Execution-Process Characteristics Among Programs That Pass Public Tests

**One-sentence claim:** Among programs that satisfy a public functional test oracle, observable execution-process characteristics contain information about subsequent failure on withheld tests that is not fully captured by public input–output behavior alone.

**What this study is:** An empirical Software Engineering study of **latent incorrectness**—functional acceptance on a visible test suite coupled with failure on a withheld suite—and whether **process observables** extracted at execution time improve prediction of that failure.

**What this study is not:** Validation of any particular benchmark methodology, LLM leaderboard extension, diversity measurement, or prompt-engineering intervention. A separate frozen instrument (INVERT Core) may be used **only** for post-hoc construct calibration and must not be tuned, adapted, or used as a success criterion for this study.

---

## 1. Motivation

Software is routinely accepted when it passes the tests available at integration time. In continuous integration, competitive programming platforms, and automated code generation pipelines, that gate is often a **subset** of the tests that will eventually govern correctness (hidden tests, production inputs, regression suites added later, or stronger oracles deployed post-merge).

When a program passes all **public** tests yet fails **withheld** tests, the failure is **latent** relative to the visible oracle: the artifact appears functionally acceptable under ordinary testing although it is not correct under a stronger criterion. This pattern is well known in principle—test inadequacy, weak oracles, and overfitting to visible cases—but it is typically discussed qualitatively or at the level of test-suite design, not as a **measurable risk signal** extractable from **how** accepted programs execute.

Two programs can produce identical outputs on every public test yet differ in control flow, resource use, stability across repeated runs, sensitivity to input perturbations, or internal execution structure. Software Engineering treats such differences as relevant to performance, reliability, maintainability, and defect risk even when I/O matches. The motivating question for LPR is whether these **execution-process characteristics** carry **predictive information** about latent failure among publicly accepted programs—information that a practitioner could use to prioritize re-testing, rejection, or further review **before** hidden tests are executed.

This question arises independently of how the programs were produced (human, generated, retrieved, or mutated). The preregistered primary analysis includes LLM-generated programs as one **stratum** because generation pipelines increasingly accept candidates on public tests only; the scientific object is the **accepted artifact**, not model ranking.

---

## 2. Research gap

| Existing line of work | What it establishes | What it does not establish |
|----------------------|---------------------|----------------------------|
| Functional testing & pass/fail oracles | Correctness relative to a given test set | Whether **process observables** predict failure on **withheld** tests among **public-pass** programs |
| pass@k and solve-rate metrics | Probability that ≥1 sample passes a test budget | Risk among **accepted** samples; prevalence of **latent incorrectness** |
| Test-suite augmentation (e.g., mutation, cross-coverage) | Methods to strengthen suites | **Prospective** predictors of hidden failure **before** suite strengthening |
| Semantic / algorithmic diversity of generated code | Cardinality of implementation families among correct samples | **Predictive** value for latent failure; not framed as SE risk |
| Dynamic stability / opcode divergence metrics | Variance among functionally correct programs | **Coupling** to withheld-test failure as primary outcome |
| Process-signature recovery benchmarks | Recoverability of named process poles under controlled contracts | **Transportability** to open competition code as **failure prediction** |

**Gap statement:** No preregistered, large-scale empirical study has tested whether **execution-process signatures** improve prediction of **latent incorrectness** (public-pass, hidden-fail) over **public I/O behavior alone** and standard syntactic baselines, on open competition-style corpora, under a frozen protocol that forbids post-hoc tuning of predictors or test splits.

---

## 3. Why existing pass@k evaluation is insufficient

pass@k estimates the probability that at least one of *k* independent samples passes all tests in a fixed evaluation harness. It is an appropriate metric for **search efficiency** and **model comparison** when the evaluation suite is treated as the ground-truth oracle.

pass@k is **insufficient** for the LPR research question for four reasons:

1. **Conditional on success.** pass@k discards all information about the **population of accepted programs**. LPR conditions on public-pass and asks which accepted programs are **unsafe** relative to withheld tests.

2. **Oracle conflation.** pass@k treats passing the evaluated suite as **correctness**. LPR explicitly separates **public** and **withheld** suites. A program contributes to pass@k on the public suite while being **latently incorrect** on the withheld suite.

3. **Process blindness.** pass@k is invariant to execution path, resource profile, and cross-run stability whenever outputs match. LPR hypothesizes that those dimensions contain **residual risk signal** not encoded in public I/O.

4. **Decision relevance.** pass@k optimizes “find any passing sample.” SE deployment optimizes “avoid accepting passing-but-wrong samples.” These objectives diverge when public suites are strict subsets of eventual oracles.

LPR does **not** propose replacing pass@k for model leaderboards. It investigates a **complementary** SE quantity: **latent failure risk among accepted candidates**.

---

## 4. Why this is a Software Engineering problem

This is a Software Engineering hypothesis because:

- **Object of study:** Programs as artifacts subject to **test oracles**, acceptance gates, and latent defects—core SE entities—not model weights or training curricula.
- **Outcome:** **Failure on withheld tests**, a standard notion of **test inadequacy** and **false acceptance**, not benchmark score.
- **Predictors:** **Execution-process observables** (traces, stability, resource profiles)—the domain of dynamic analysis and operational qualification—not prompt templates or diversity indices.
- **Practical stake:** CI/CD and automated merging increasingly auto-accept on partial test coverage; **ranking accepted builds by latent risk** is an SE decision problem.
- **Generalizability claim:** Results are intended to hold for **any** source of programs passing public tests, with LLM generation as one preregistered stratum.

The study does **not** ask which LLM is best. It asks whether **process information** refines **accept/reject** among programs already cleared by public functional tests.

---

## 5. Research questions

| ID | Question |
|----|----------|
| **RQ1 (Primary)** | Among programs that pass all public tests, do execution-process signatures improve prediction of failure on withheld tests compared to public I/O behavior alone? |
| **RQ2** | Which preregistered process-signature dimensions (if any) contribute incremental predictive information after controlling for public I/O equivalence? |
| **RQ3** | Does a frozen process-based risk score reduce the rate of accepting latently incorrect programs at a fixed candidate budget compared to accepting all public-pass programs (a **virtual process gate**)? |
| **RQ4** | Does predictive utility differ across preregistered problem strata (e.g., difficulty, algorithmic tag, presence of output checkers)? |
| **RQ5 (Exploratory, labeled)** | Do process dimensions that discriminate known process poles on a **frozen external calibration corpus** (INVERT Core exports, read-only) correlate with dimensions that predict latent failure in LPR? *This RQ does not define study success.* |

---

## 6. Hypotheses

### Primary hypothesis (H1)

Among programs that pass all public tests, process signatures contain **incremental predictive information** about withheld-test failure beyond public I/O signatures:

- **H1a:** The preregistered **Process Risk Model** achieves a higher area under the ROC curve (AUC) for predicting latent incorrectness than the **I/O Baseline Model** on the **primary holdout corpus**, with ΔAUC ≥ **0.05** (absolute).
- **H1b:** The improvement in H1a remains **positive** (ΔAUC > 0) after adjustment for preregistered syntactic covariates in the **primary model specification**.

### Secondary hypotheses

- **H2 (Stability stratum):** Incremental AUC is larger for problems where public-pass programs show higher **cross-run process instability** (preregistered definition) than for problems with low instability.
- **H3 (Checker stratum):** Incremental AUC is larger on problems with **output checkers** or multiple valid outputs than on strict single-output problems.
- **H4 (Source stratum):** The H1a effect direction is **consistent** (same sign of ΔAUC) across at least two of three preregistered program-source strata: human-submitted, LLM-generated, and mined historical submissions.
- **H5 (Virtual gate):** At a preregistered candidate budget *k*, ranking public-pass candidates by ascending process risk yields a **lower latent incorrectness rate** among accepted programs than uniform random acceptance among public-pass candidates.

### Null hypotheses (explicit)

- **H0a:** ΔAUC = 0 between Process Risk Model and I/O Baseline Model on the primary holdout.
- **H0b:** Process signatures are **redundant** with public I/O after syntactic adjustment (coefficient vector for process dimensions jointly zero in preregistered logistic model).

**Interpretation:** Rejecting H0a via H1a is **necessary** but not sufficient for a strong SE claim; effect size, calibration, and stratum robustness are reported in full.

---

## 7. Variables

### Study unit

The **program instance** is the unit of analysis: one executable solution for one problem, from one preregistered source stratum, evaluated under the frozen public/withheld split.

### Problem-level covariates (fixed at registration)

- Corpus identifier (development vs holdout)
- Algorithmic / skill tag (from dataset metadata)
- Difficulty bin (dataset-native)
- Checker presence (binary, rule-based from metadata)
- Public-test count; withheld-test count
- Human reference solution count (metadata only; not used as labels)

### Program-level covariates

- Source stratum (human / LLM / mined)
- Generator model ID (LLM stratum only)
- Sampling temperature (LLM stratum only)
- Public-pass indicator (inclusion gate: must be true)
- Withheld-pass indicator (**primary label** for latent incorrectness)

---

## 8. Independent variables

*Predictors and design factors—not manipulated in an RCT sense but fixed by preregistration.*

| Variable | Role | Levels / definition |
|----------|------|---------------------|
| **Process signature vector** | Primary predictor bundle | Preregistered dimensions in §9; extracted **before** label access on holdout |
| **Public I/O signature** | Baseline predictor | Hash or vector of outputs on all public tests |
| **Syntactic signature** | Covariate / baseline | Preregistered static representation (no learned tuning on holdout) |
| **Corpus** | Design factor | Development (calibration) vs primary holdout |
| **Source stratum** | Design factor | Human, LLM-generated, mined submissions |
| **Problem stratum** | Subgroup factor | Tags, difficulty, checker presence |
| **LLM model** | Factor (LLM stratum) | Fixed list locked at registration |
| **Temperature** | Factor (LLM stratum) | {0.0, 0.4, 0.8} — no intermediate values added post hoc |

**Frozen split rule:** Public vs withheld tests are assigned by a **deterministic, problem-level rule** fixed before any model generation or signature extraction. The rule is: **first 20% of tests by dataset order** = public; **remaining 80%** = withheld. No rebalancing after observing failure rates.

---

## 9. Dependent variables

| Variable | Definition |
|----------|------------|
| **Latent incorrectness** (primary label) | `public_pass = TRUE` AND `withheld_pass = FALSE` |
| **Latent correct** | `public_pass = TRUE` AND `withheld_pass = TRUE` |
| **Outright fail** | `public_pass = FALSE` (excluded from primary analysis population) |
| **Hidden failure rate** | Proportion latent incorrect among public-pass, per problem × stratum |
| **Acceptance outcome (virtual gate)** | Whether a program would be accepted under preregistered selection policy at budget *k* |

---

## 10. Primary outcome

**ΔAUC on primary holdout:** Difference in AUC for predicting latent incorrectness between:

1. **Process Risk Model** — preregistered supervised model using process signature dimensions + public I/O signature  
2. **I/O Baseline Model** — public I/O signature only  

Both models fit **only** on the development corpus; evaluated **once** on the primary holdout without retraining.

**Primary estimand:** Mean ΔAUC across all public-pass program instances in the holdout, with **problem-level cluster bootstrap** 95% confidence interval.

---

## 11. Secondary outcomes

| Outcome | Purpose |
|---------|---------|
| AUC of Syntax Baseline Model | Dissociation from surface form |
| Brier score / calibration slope | Decision quality, not only ranking |
| ΔAUC on secondary holdout corpus | Generalization across datasets |
| Per-dimension ablation ΔAUC | Attribution (pre-specified dimensions only) |
| Latent incorrectness rate under virtual gate vs random | RQ3 |
| Interaction ΔAUC by checker / difficulty stratum | RQ4 |
| False acceptance reduction at fixed recall | SE operationalization |
| Prevalence of latent incorrectness among public-pass | Descriptive base rate (not a success criterion) |

---

## 12. Inclusion criteria

### Problems

- Open-license competition-style problem with ≥ **100** total tests in dataset harness  
- Executable Python 3 reference environment compatible with preregistered sandbox  
- Problem appears in exactly one of the two preregistered corpora (no duplicate statements across corpora)  
- Metadata includes at least one skill / algorithm tag  

### Programs (analysis population)

- Passes **100%** of public tests under sandbox limits  
- Completes process-signature extraction without sandbox timeout on **all** public tests  
- Source stratum is one of the preregistered strata  
- For LLM stratum: produced by a preregistered model with preregistered decoding parameters  

### Corpora (locked at registration)

- **Development corpus:** BAAI/TACO — test split, filtered by inclusion rules, target **N = 1,200** problems  
- **Primary holdout corpus:** CodeContests+ Verified subset — target **N = 800** problems  
- **Secondary holdout:** Remaining eligible TACO test problems not in development draw (if any), reported separately  

---

## 13. Exclusion criteria

- Problems with < 100 tests or non-Python primary solutions in harness  
- Problems with documented broken tests or withdrawn status in dataset errata (list frozen at registration)  
- Programs exceeding sandbox resource ceilings (marked `execution_incomplete`, excluded from primary analysis)  
- Programs that read external files, use network, or violate sandbox policy  
- Duplicate normalized source within (problem, stratum, model) — **first execution order retained**, duplicates dropped (rule fixed)  
- Any problem for which public/withheld split yields < 20 public or < 50 withheld tests  
- Post-hoc exclusion of strata, models, or problems based on observed effect direction  

---

## 14. Planned statistical analysis

*All analysis scripts will be versioned; primary analysis run **once** on locked holdout labels.*

### 14.1 Primary analysis (H1a)

1. Fit **I/O Baseline Model** (logistic regression with problem fixed effects optional per sensitivity — preregistered: **primary spec uses random intercept per problem via mixed model**) on development public-pass set.  
2. Fit **Process Risk Model** = I/O + preregistered process dimensions (standardized on development only).  
3. Compute AUC on holdout public-pass set for both models.  
4. **ΔAUC** = AUC_process − AUC_IO.  
5. **Inference:** Problem-cluster bootstrap, **B = 2,000** resamples; two-sided 95% CI.  
6. **Hypothesis test:** H1a supported if lower bound of CI for ΔAUC ≥ 0.05.

### 14.2 Adjustment analysis (H1b)

- Nested model comparison: Syntax + I/O vs Syntax + I/O + Process (likelihood ratio test on development; holdout ΔAUC reported).  
- No variable selection; all preregistered dimensions enter.

### 14.3 Virtual gate (H5)

- For each problem with ≥ *k* public-pass LLM samples (*k* ∈ {1, 5, 10}, preregistered):  
  - **Policy A:** Accept *k* lowest process-risk scores.  
  - **Policy B:** Accept *k* uniform random public-pass.  
- Compare latent incorrectness rate; report paired bootstrap by problem.

### 14.4 Strata (H2–H4)

- Pre-specified subgroups; no fishing.  
- Report ΔAUC per subgroup with multiplicity control **Benjamini–Hochberg FDR** across **M = 8** preregistered subgroup tests.

### 14.5 Exploratory RQ5 (INVERT calibration)

- Correlate **rank-order** of dimension predictive coefficients (holdout) with **rank-order** of dimension pole-separation statistics on frozen INVERT Core export re-profiling.  
- **Not** used in GO/NO-GO.  
- **No** detector or threshold tuning on LPR labels.

### 14.6 Missing data

- Listwise deletion for incomplete signatures; report attrition table.  
- Sensitivity: worst-case bounds if attrition > 10%.

### 14.7 Power (planned, not post-hoc)

- Development corpus used for variance estimation only.  
- Minimum detectable ΔAUC **0.03** at 80% power assumed for holdout public-pass *n* ≥ 50,000 instances (compute budget supports; if not met, report underpowered honestly).

---

## 15. Threats to validity

| Threat | Mitigation (preregistered) |
|--------|---------------------------|
| **Construct:** latent incorrectness ≠ real-world bug | Frame as **withheld-test proxy**; secondary outcome on efficiency regression where available |
| **Construct:** process signature mis-specified | Multiple preregistered dimensions; ablation pre-specified; no post-hoc dimensions |
| **Internal:** leakage across public/withheld | Signatures extracted using **public tests only**; withheld used **only** for label |
| **Internal:** duplicate problems across corpora | Statement-hash deduplication before registration lock |
| **Conclusion:** overfitting predictors | Train on development only; **single** holdout evaluation |
| **Conclusion:** LLM-specific artifact | Human and mined strata test generalization |
| **External:** sandbox ≠ production | Discuss; no over-claim on deployment |
| **External:** Python competition code only | Scope statement; no claim on all languages |
| **Statistical:** multiple comparisons | FDR on subgroup suite; primary hypothesis untouched |
| **Collaboration:** INVERT instrument bias | RQ5 exploratory; success not tied to INVERT recovery rates |
| **Generative:** temperature confound | Report LLM stratum with temperature as factor; not primary estimand |

---

## 16. Compute budget

*Budget declaration for reproducibility; not a success criterion.*

| Stage | Resource | Estimate |
|-------|----------|----------|
| Sandbox execution | CPU cluster, 4 GB RAM / program, 30s timeout / test | ≤ 3M program executions |
| LLM generation | 8 open models × 50 samples × 1,200 problems × 3 temperatures | ≤ 1.44M completions |
| Signature extraction | ≤ 2× execution cost (multi-run stability) | ≤ 6M sandbox runs |
| Storage | Raw logs + signature tables | ≤ 5 TB |
| Analysis | Offline; bootstrap B=2000 | ≤ 500 CPU-hours |

**Ceiling:** If generation completes under budget, **no additional models or temperatures** may be added. If over budget, reduce LLM problems proportionally by **pre-registered random seed** (not by difficulty or failure rate).

---

## 17. Expected negative outcomes

These outcomes are **valid scientific results**, not protocol failures:

1. **ΔAUC ≈ 0:** Process signatures add no predictive information beyond public I/O on holdout.  
2. **Reverse stratum effects:** Process signal present only for LLM, absent for human submissions.  
3. **Single-dimension dominance:** Only stability dimension carries signal; others null.  
4. **Low prevalence:** Latent incorrectness rate among public-pass < 2% on holdout (ceiling effect on AUC).  
5. **Virtual gate ineffective:** Risk ranking does not beat random at practical *k*.  
6. **RQ5 null:** INVERT calibration dimensions uncorrelated with LPR predictive dimensions.  
7. **Syntax absorbs process:** Process incremental ΔAUC vanishes after syntactic covariates.

Each negative outcome will be reported with equal prominence to positive results.

---

## 18. Explicit GO / NO-GO criteria

*Applied after primary holdout analysis only. No interim peeking at holdout labels for protocol changes.*

### GO (proceed to full write-up as confirmatory SE study)

**All** of:

- [ ] Primary holdout ΔAUC lower 95% CI bound ≥ **0.05** (H1a)  
- [ ] Holdout ΔAUC point estimate > 0 in **≥ 2** of 3 source strata  
- [ ] Virtual gate at *k* = 5 reduces latent incorrectness rate by ≥ **10% relative** vs random (median across problems)  
- [ ] Attrition from signature extraction ≤ **10%** of public-pass instances  
- [ ] No preregistered exclusion rule violated post hoc  

### NO-GO (publish results as null / boundary study; do not upgrade claims)

**Any** of:

- [ ] Primary ΔAUC CI includes zero or upper bound < 0.05  
- [ ] Process dimensions jointly non-significant in holdout-adjusted model **and** ΔAUC < 0.02  
- [ ] Virtual gate ineffective (relative reduction < 5% at *k* = 5)  
- [ ] Attrition > 10% without sensitivity bounds supporting robustness  

### STOP (integrity failure — do not publish confirmatory claims)

**Any** of:

- [ ] Public/withheld split altered after label inspection  
- [ ] Predictor set altered after holdout evaluation  
- [ ] Holdout problems or models added/removed based on observed effects  
- [ ] Undocumented multiple re-evaluation of holdout  

---

## 19. Success criteria

**Scientific success** (independent of GO/NO-GO):

- Locked OSF registration timestamp **before** holdout label analysis.  
- Complete attrition and execution audit trail.  
- Reproducible signature extraction specification (documented separately from this preregistration).  
- Public release of analysis population table and analysis code.

**Confirmatory success** (GO met):

- Demonstrated **incremental** predictive value of process signatures for latent incorrectness on independent holdout at preregistered effect threshold.  
- Demonstrated **operational** value via virtual process gate at small *k*.

---

## 20. Failure criteria

**Study design failure:**

- Inability to obtain ≥ 30,000 public-pass holdout instances after preregistered exclusions.  
- Sandbox incompatibility with > 25% of problems despite preregistered filters.  
- Corpus license change prohibiting redistribution.

**Scientific failure (informative null):**

- GO criteria not met (see §18).  
- Process signal indistinguishable from I/O baseline.

**Integrity failure:**

- Any item in STOP list (§18).

---

## 21. Claims that WILL be allowed

*Only if supported by preregistered primary analysis on holdout.*

- Among programs passing all public tests, a **preregistered** process signature improves prediction of failure on withheld tests compared to public I/O alone, with reported ΔAUC and CI.  
- Specific preregistered process dimensions contribute **incremental** information (with ablation table).  
- A frozen process-risk ranking **can reduce** acceptance of latently incorrect programs at fixed budget *k* relative to random acceptance among public-pass programs (virtual gate).  
- Latent incorrectness among public-pass programs occurs at rate *p* on holdout (descriptive).  
- Effects differ across **preregistered** strata (with FDR).  
- Results apply to **test-suite structure** (public ⊂ full), not to LLM leaderboard performance.  
- Exploratory correlation between LPR predictive dimensions and INVERT Core calibration dimensions (RQ5), labeled exploratory.

---

## 22. Claims that WILL NOT be allowed

*Regardless of observed data.*

- That this study **validates INVERT** or any detector / benchmark methodology.  
- That INVERT recovery rates **cause** or **prove** LPR findings.  
- That any LLM is **better** or **worse** than another (no model leaderboard claims).  
- That process signatures **replace** withheld tests or **guarantee** correctness.  
- That results establish **diversity**, algorithmic cardinality, or thin-manifold hypotheses.  
- That prompt wording **caused** process risk (no prompt-engineering claims; prompts fixed and reported as nuisance factors in LLM stratum).  
- That findings **generalize** to all software domains, languages, or production systems without qualification.  
- That post-hoc **optimized** predictors, splits, or dimensions represent confirmatory evidence.  
- That unpublished exploratory analyses support **confirmatory** conclusions.  
- That a **benchmark paper** contribution is made (no new leaderboard, no new tasks).  

---

## Process signature dimensions (locked names only)

*Operational definitions deferred to a separate extraction specification. Names and count are frozen.*

| ID | Dimension name (frozen) | Extraction uses public tests only |
|----|-------------------------|-----------------------------------|
| P1 | `public_io_signature` | Yes (baseline component) |
| P2 | `cross_run_output_stability` | Yes |
| P3 | `cross_run_trace_stability` | Yes |
| P4 | `resource_profile_dispersion` | Yes |
| P5 | `cross_input_signature_entropy` | Yes |
| P6 | `local_pool_stereotypy` | Yes (within problem × source × model pool) |
| P7 | `opcode_profile_signature` | Yes |

**Syntactic covariate (baseline):** `syntax_embedding_cluster_id` from frozen featurizer fit on development only.

No additional dimensions may be added after holdout labels are analyzed.

---

## LLM stratum protocol (nuisance design, not intervention)

- **Purpose:** Supply one source of public-pass programs; **not** an prompt-optimization study.  
- **Prompt template:** Single fixed template per problem (dataset statement + function signature); **no** pole-naming, **no** process instructions, **no** chain-of-thought requirement.  
- **Models (frozen list):** To be enumerated in OSF component `models.yaml` before generation.  
- **Decoding:** temperature ∈ {0.0, 0.4, 0.8}, top-p = 0.95, max tokens fixed.  
- **No** prompt changes after pilot ≤ 50 problems. Pilot assesses **execution feasibility only**, not effect sizes.

---

## Human and mined strata

- **Human:** Accepted historical submissions from open corpora (same problems as LLM stratum where available).  
- **Mined:** Additional accepted submissions not used for generation; no authorship inference claims.  
- No human annotation of process labels.

---

## INVERT Core reference (calibration only)

- **Role:** Frozen external instrument for **RQ5 exploratory** construct alignment only.  
- **Permitted:** Re-profile stored artifacts from frozen INVERT Core generalization exports with the **same** LPR signature extractors (where applicable).  
- **Prohibited:** Modifying INVERT Core, detectors, benchmarks, prompts, thresholds, or using INVERT recovery rate as LPR outcome.  
- **Prohibited:** Tuning LPR predictors to maximize correlation with INVERT poles.

---

## Prohibited practices (binding)

The following are **explicitly forbidden** after registration timestamp:

1. **Detector tuning** after seeing results (no INVERT detector changes at all).  
2. **Benchmark adaptation** (no changes to INVERT benchmarks or LPR corpora selection rules based on holdout effects).  
3. **Prompt optimization** after feasibility pilot.  
4. **Hidden protocol changes** (splits, timeouts, dimensions, models, temperatures, exclusions).  
5. **Changing variables** after analysis (outcomes, predictors, populations, success thresholds).  
6. **Holdout re-evaluation** with altered models after observing ΔAUC.  
7. **Selective reporting** of subgroups with favorable ΔAUC without full FDR table.  
8. **Claiming validation of INVERT** from LPR outcomes.

Violations trigger **STOP** status (§18) and require transparent disclosure if any analysis occurred.

---

## Registration checklist (before any code)

- [ ] OSF project created; this document deposited as PDF/Markdown snapshot  
- [ ] `models.yaml`, `corpus_filters.yaml`, `split_rule.yaml` deposited  
- [ ] Author list and affiliations complete  
- [ ] IRB / ethics: not required (public artifacts, no human subjects)  
- [ ] Timestamp recorded; no holdout labels inspected  

---

## Document history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-29 | Initial preregistration |

---

*End of preregistration. No implementation, results, or algorithms are defined herein beyond frozen variable names and analysis plan.*
