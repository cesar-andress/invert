# LPR Dataset Protocol

**Study ID:** `LPR-2026-001`  
**Document:** `DATASET_PROTOCOL.md`  
**Version:** 1.0  
**Status:** FROZEN — audit before data collection  
**Date:** 2026-06-29  
**Repository:** `cesar-andress/invert`  
**Protocol lock:** `PROTOCOL_LOCK.json` (git commit hash obligatorio)
**Companion artifacts:**

| File | Purpose |
|------|---------|
| `PREREGISTRATION.md` | Study hypotheses and analysis plan |
| `benchmark_inventory.csv` | Literature/repo inventory of candidate corpora |
| `corpus_filters.yaml` | Frozen inclusion/exclusion and execution policy |
| `split_rule.yaml` | Deterministic public/withheld test partition |
| `dataset_go_no_go.json` | Objective proceed/halt criteria |

**Scope:** This protocol governs **dataset selection, filtering, and test partitioning only**. It does not define process signatures, statistical models, detectors, or analysis code. No experimental results inform this document.

---

## 0. Protocol audit statement

This protocol is written to be reviewed **before any data row is executed**, **before any holdout label is inspected for analysis**, and **before any feasibility pilot reads latent-incorrectness rates for protocol modification**.

Auditors should verify:

1. Primary and holdout corpora are named and justified from inventory evidence, not from pilot outcomes.  
2. Every exclusion rule maps to a machine-logged `exclusion_code`.  
3. Public/withheld assignment is a function of test indices only.  
4. No INVERT Core artifact is required to execute this protocol.

---

## 1. Motivation (dataset layer)

Latent Process Risk (LPR) requires corpora where:

- Programs can be executed against a **large** bundled test suite.  
- The suite can be partitioned into **public** (visible at acceptance time) and **withheld** (stronger oracle) **without** native platform hidden tests.  
- **Ground-truth labels** for latent incorrectness are derivable as: `pass(public) ∧ ¬pass(withheld)`.  
- **Human historical solutions** exist without manual annotation.  
- Licenses permit redistribution and research use without ShareAlike contamination of derivatives.

The dataset protocol therefore prioritizes **test depth**, **label definability**, **execution reproducibility**, and **holdout independence** over benchmark popularity.

---

## 2. Dataset inventory method

Inventory was assembled from:

- Hugging Face dataset cards and pinned README files  
- Original papers (TACO arXiv:2312.14852; APPS NeurIPS 2021; CodeContests+ EMNLP 2025 Findings; CodeContests/AlphaCode; CodeNet OpenReview; LiveCodeBench arXiv:2403.07974; BigCodeBench arXiv:2406.15877)  
- Official GitHub repositories and maintenance status  
- Third-party harness analyses (e.g., CodeContests false-negative studies)

**No dataset was executed for this inventory.** Counts marked `est` are from authoritative dataset documentation, rounded for planning.

Full rows: `benchmark_inventory.csv`.

---

## 3. Inclusion criteria (explicit)

A problem **enters the candidate pool** iff **all** of the following hold:

| ID | Criterion |
|----|-----------|
| IC-01 | **Open license** allowing research use and redistribution without ShareAlike obligation on LPR derivatives |
| IC-02 | **Executable Python 3** solution path (standalone script or `fn_name` function entry) |
| IC-03 | **Deterministic** judging under frozen sandbox (`PYTHONHASHSEED=0`; no unseeded randomness requirement) |
| IC-04 | **Bundled tests** parseable offline into atomic `(input, output)` cases or checker-backed cases |
| IC-05 | **≥ 100** atomic bundled tests (pre-partition) |
| IC-06 | **Held-out split reproducible** via `split_rule.yaml` (not dependent on platform secret tests) |
| IC-07 | **No interactive** or **file-IO-only** judging in v1 |
| IC-08 | **No manual annotation** required for labels |
| IC-09 | **Algorithm/skill tag** present in metadata for stratified sampling |
| IC-10 | **Offline sandbox** execution possible (no proprietary judge APIs) |

Programs (later phase) additionally require public-pass for the analysis population; that filter is **not** a problem-level inclusion criterion.

---

## 4. Exclusion criteria (explicit)

A candidate problem is **excluded** if **any** condition holds (see `corpus_filters.yaml` for codes):

| ID | Criterion | Code |
|----|-----------|------|
| EC-01 | Fewer than 100 atomic tests | `INCOMPLETE_TESTS` |
| EC-02 | Interactive judge | `INTERACTIVE` |
| EC-03 | Non-Python or non-executable template | `UNSUPPORTED_LANGUAGE` |
| EC-04 | Declared nondeterministic judging without fixed seed | `NONDETERMINISTIC` |
| EC-05 | Unparseable harness / missing I/O | `MISSING_HARNESS` |
| EC-06 | Post-split public < 20 or withheld < 50 | `SPLIT_INSUFFICIENT_COUNTS` |
| EC-07 | Duplicate statement fingerprint across primary and holdout | `DUPLICATE_STATEMENT` |
| EC-08 | Forbidden unsupported features (network, threading, etc.) | `UNSUPPORTED_*` |
| EC-09 | CC+ holdout: TPR < 0.9 or TNR < 0.9 | `CCPLUS_BELOW_VERIFIED_THRESHOLD` |
| EC-10 | TACO: invalid `input_output` JSON | `TACO_INVALID_IO_JSON` |

**Post-collection exclusion based on latent-incorrectness rate is prohibited.**

---

## 5. Primary dataset recommendation

### **PRIMARY_DEVELOPMENT: BAAI/TACO (`test` split)**

| Factor | Evidence |
|--------|----------|
| Scale | 1,000 test-split problems; target 1,200 sampled from eligible pool with stratification (preregistration allows up to full eligible test split) |
| Tests | Literature and TACO paper cite **~200** tests/problem on test split; satisfies IC-05 |
| Human solutions | **~1.55M** solutions corpus-wide; multiple Python solutions per problem in metadata |
| Python focus | Collection emphasizes Python 3 solutions |
| License | Apache 2.0 with documented upstream mix; **no ShareAlike** (unlike APPS) |
| Harness | JSON `input_output` pairs; widely used with reference metric scripts |
| Metadata | `skill_types`, `tags`, `difficulty` for outcome-blind stratification |
| Role | **Development / predictor fitting / split manifest validation** |

**Why not train split:** Train split is exposed in countless LLM training pipelines → higher contamination for generated-solution stratum. Test split is the preregistered LPR development corpus.

**Engineering effort:** Medium — HF-native, JSON tests, no Riegeli/protobuf.

---

## 6. External holdout recommendation

### **HOLDOUT_PRIMARY: ByteDance-Seed/Code-Contests-Plus — Verified subset**

| Factor | Evidence |
|--------|----------|
| Test quality | **TPR and TNR > 0.9** per problem on Verified subset (EMNLP 2025 Findings); reduces **false latent labels** from bad tests |
| Scale | 11,690 problems full set; Verified subset smaller but sufficient for target **800** problems |
| Tests | ~**200** cases/problem average; generator-validated |
| Checkers | Output checkers on multi-answer problems → correct **behavioral equivalence** class, not single canonical string |
| Human solutions | **13M+** correct and incorrect submissions for mined/human strata |
| License | **CC-BY-4.0** — open, no ShareAlike |
| Independence | Different curation pipeline from TACO; statement-level dedup vs TACO per `split_rule.yaml` |
| Role | **Single primary holdout** for confirmatory label integrity assessment (not predictor training) |

**Why Verified:** Latent incorrectness labels are only as sound as withheld tests. CodeContests (original) documents false negatives on correct solutions; CC+ explicitly measures TPR/TNR and publishes Verified filter.

**Engineering effort:** High — larger artifacts, checker/generator semantics, sandbox parity with SandboxFusion-style evaluation.

---

## 7. Evidence-based rejection of alternatives

| Dataset | Why not primary/holdout |
|---------|-------------------------|
| **APPS** | CC-BY-SA 3.0 conflicts with `share_alike_allowed: false`; ~21 tests/problem fails IC-05 without excluding most problems |
| **CodeContests (DeepMind)** | Repo archived; known test false negatives; superseded by CC+ |
| **CodeNet** | Full per-problem test suites not uniformly bundled; very high harness reconstruction effort |
| **HumanEval / HumanEval+ / MBPP** | Far below 100 tests/problem; toy N; unsuitable latent-error prevalence estimation |
| **LiveCodeBench** | Hidden tests not fully open; temporal contamination design conflicts with frozen index split transparency |
| **BigCodeBench** | ~5.6 tests/task; library-heavy flaky tests; wrong task class (API micro-tasks) |
| **EffiBench** | Efficiency axis; single optimal human ref; optional secondary only |
| **Community scrapes** | License fragmentation; poor reproducibility |

---

## 8. Split rule summary

**Authoritative specification:** `split_rule.yaml`

| Parameter | Value |
|-----------|-------|
| Public fraction | 20% (floor) |
| Withheld fraction | 80% (remainder) |
| Index rule | `public = {0 .. floor(0.2N)−1}` on deterministically ordered atomic tests |
| Ordering | Dataset-native order; tie-break SHA256(input) ascending |
| Cross-corpus dedup | Drop holdout if statement fingerprint matches primary |

### Why this prevents p-hacking

1. **Outcome-blind:** Partition uses `(N, index)` only — never pass rates or latent prevalence.  
2. **Model-blind:** No access to LLM/human submissions when assigning tests.  
3. **No adaptive ratios:** 20/80 fixed; no search over public fractions.  
4. **No difficulty rerouting:** EASY/HARD tags excluded from index assignment.  
5. **Pre-registered holdout corpus:** CC+ Verified chosen before holdout label analysis.  
6. **Mechanical exclusions only:** Low test count rules do not target label balance.  
7. **Auditable manifest:** `split_manifest.json` hashes rules + dataset revisions for third-party replay.

---

## 9. Corpus filters summary

**Authoritative specification:** `corpus_filters.yaml`

| Policy area | Frozen choice |
|-------------|---------------|
| Language | Python 3.10 sandbox |
| Min tests | 100 total; 20 public / 50 withheld post-split |
| Timeouts | 30s/test; 600s/program |
| Memory | 4096 MB |
| Duplicates | Normalized source SHA256 within bucket; statement hash across corpora |
| Sampling seed | `20260629` |
| Targets | 1,200 primary / 800 holdout problems |
| Logging | Every exclusion → `exclusions.jsonl` with code |

---

## 10. GO / NO-GO summary

**Authoritative specification:** `dataset_go_no_go.json`

| Decision | Condition |
|----------|-----------|
| **GO** | All G1–G10 met; no N1–N8; no STOP |
| **NO-GO** | Any failure of minimum problem counts, harness viability, or latent signal in feasibility pilot |
| **STOP** | Any post-lock protocol tampering |

Key numeric gates:

- ≥ **1,000** eligible primary problems (target 1,200)  
- ≥ **650** eligible holdout problems (target 800)  
- ≤ **35%** problem exclusion rate  
- ≥ **85%** reference public-pass rate in pilot  
- Latent incorrectness observable in pilot (≥2% reference rate **or** ≥5 problems with reference latent fail)  
- **100%** exclusions logged  

---

## 11. Data collection phases (documentation only)

| Phase | Action | Outcome |
|-------|--------|---------|
| 0 | Protocol audit + OSF lock | Hashes recorded |
| 1 | Pin HF revisions; build split manifest | `split_manifest.json` |
| 2 | Feasibility pilot (50+50 problems) | GO/NO-GO decision |
| 3 | Full problem sampling per stratification | Frozen problem list |
| 4 | Program collection (human/mined/LLM) | Separate protocol; not in this document |
| 5 | Integrity checks I1–I3 | No corpus changes |

---

## 12. Relationship to INVERT Core

INVERT Core is **not** part of this dataset protocol.

- No INVERT benchmark tasks are used as LPR problems.  
- No INVERT detectors define dataset inclusion.  
- INVERT may appear later only in **RQ5 exploratory calibration** (preregistration), using frozen exports and the **same** public-test execution environment where applicable.

---

## 13. Prohibited actions (binding)

The following are **forbidden** after protocol lock:

1. Inspecting holdout latent-incorrectness rates **before** split manifest is frozen  
2. Changing `public_fraction`, `minimum_total_tests`, or Verified TPR/TNR thresholds based on outcomes  
3. Moving problems between primary and holdout based on effect sizes  
4. Adding HumanEval/MBPP/APPS as holdout replacements without new OSF registration  
5. Dropping exclusion codes or failing to log exclusions  
6. Tuning timeouts to increase public-pass rate  
7. Any modification to INVERT Core, detectors, or benchmarks motivated by LPR dataset statistics  

---

## 14. Auditor checklist

- [ ] `benchmark_inventory.csv` covers ≥12 corpora with suitability ratings  
- [ ] Primary = TACO test; Holdout = CC+ Verified — justified in §5–6  
- [ ] `split_rule.yaml` is deterministic and outcome-blind  
- [ ] `corpus_filters.yaml` lists every exclusion code and logging requirement  
- [ ] `dataset_go_no_go.json` has numeric thresholds and STOP conditions  
- [ ] No section references experimental results or computed statistics  
- [ ] CC-BY-SA corpora excluded as primary due to license policy  
- [ ] Minimum 100 tests/problem enforced  

---

## 15. Document history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-29 | Initial frozen dataset protocol |

---

*End of dataset protocol. No software, detectors, or experimental results are defined or reported herein.*
