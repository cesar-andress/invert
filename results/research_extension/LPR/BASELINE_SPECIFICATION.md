# LPR Baseline Comparison Protocol: Specification

**Study ID:** `LPR-2026-001`  
**Document:** `BASELINE_SPECIFICATION.md`  
**Version:** 1.0  
**Status:** FROZEN — before EPS extraction and before hidden-label analysis  
**Date:** 2026-06-29  
**Repository:** `cesar-andress/invert`  
**Locks:** `EPS_LOCK.json` (`aa6be10…`), `PROTOCOL_LOCK.json` (`ff45009…`)

---

## 0. Purpose

Hostile reviewers will argue that **External Process Signature (EPS)** is disguised **syntax**, **AST**, or **embedding** similarity. This document **freezes** mandatory **non-process baselines** and the **primary comparison protocol** so that LPR success requires EPS to add predictive value **beyond** frozen non-process representations.

**Primary research question (comparison):**

> Does EPS improve prediction of **latent incorrectness** among **public-pass** programs beyond non-process representations?

---

## 1. Objects and notation

| Symbol | Definition |
|--------|------------|
| `π` | Program source + entry point |
| `𝒯_pub`, `𝒯_hid` | Public / withheld test sets (`split_rule.yaml`) |
| `y(π)` | **Latent label:** `1` if `pass(π,𝒯_pub) ∧ ¬pass(π,𝒯_hid)`; `0` if pass both; excluded otherwise |
| `B_k(π)` | Baseline feature map `k` (non-process unless noted) |
| `EPS(π)` | Frozen 7-tuple `(P1,…,P7)` per `EPS_SPECIFICATION.md` |
| `P1(π)` | Public I/O signature (conductual; **not** process) |

**Leakage rule:** No baseline or EPS feature may read `𝒯_hid`, `y(π)`, or outcomes on withheld tests **during feature extraction**. Labels used **only** in downstream supervised fitting/evaluation stages declared in `PREREGISTRATION.md`.

---

## 2. Mandatory baseline families

### Family F1 — Size / surface (`B_SIZE`)

| ID | Feature | Definition |
|----|---------|------------|
| B_SIZE_01 | `src_char_count` | `|π|` UTF-8 NFKC chars |
| B_SIZE_02 | `src_line_count` | newline-split lines |
| B_SIZE_03 | `src_token_count` | `len(tokenize(π))` |
| B_SIZE_04 | `comment_line_count` | lines matching `^\s*#` |
| B_SIZE_05 | `cyclomatic_complexity` | McCabe on AST (automatic) |
| B_SIZE_06 | `function_def_count` | `ast.FunctionDef` + `AsyncFunctionDef` |
| B_SIZE_07 | `import_count` | `ast.Import` + `ast.ImportFrom` nodes |

**Representation:** `z_SIZE(π) ∈ ℝ^7` (standardized on development).

### Family F2 — AST / structural (`B_AST`)

| ID | Feature | Definition |
|----|---------|------------|
| B_AST_01 | `ast_node_histogram` | Count vector over **frozen** 24 AST node types |
| B_AST_02 | `ast_max_depth` | max depth of AST tree |
| B_AST_03 | `ast_normalized_hash` | SHA-256 of canonical `ast.dump(annotate_fields=False)` |
| B_AST_04 | `cfg_node_count` | basic blocks via `ast` walk (approximate CFG nodes) |
| B_AST_05 | `ast_branch_count` | `If` + `For` + `While` + `ExceptHandler` counts |

**Pairwise distance (diagnostic only, not primary model):** normalized tree edit distance `d_AST` optional in ablation B-AST-PAIR.

**Program-level vector:** `z_AST(π) = concat(hist, scalars)` ∈ ℝ^{24+4} after hashing to 8-bin sketch for hash dimension.

### Family F3 — Token / lexical (`B_TOK`)

| ID | Feature | Definition |
|----|---------|------------|
| B_TOK_01 | `bow_token_freq` | Bag-of-tokens over `tokenize(π)`, top-512 frozen vocab from **development** |
| B_TOK_02 | `bigram_hash_sketch` | 256-bin hash sketch of token bigrams |
| B_TOK_03 | `trigram_hash_sketch` | 256-bin hash sketch of token trigrams |
| B_TOK_04 | `identifier_normalized_bow` | BOW after renaming identifiers to `VAR{i}` in order |

**Vector:** `z_TOK(π) ∈ ℝ^{512+256+256}` sparse-dense hybrid stored as fixed-length.

### Family F4 — Bytecode static (`B_BC`) — **no execution**

Computed via `compile(π)` + `dis.get_instructions` on **source** (static compile), **not** hidden tests.

| ID | Feature | Definition |
|----|---------|------------|
| B_BC_01 | `static_opcode_histogram` | counts over CPython 3.10 opcode names, 32-bin map shared with EPS categories |
| B_BC_02 | `static_instruction_count` | total instructions |
| B_BC_03 | `static_branch_opcode_count` | `POP_JUMP_*`, `JUMP_*` |

**Vector:** `z_BC(π) ∈ ℝ^{34}`.

**Note:** Distinct from EPS P7 which uses **runtime** opcode PMF on **public tests**.

### Family F5 — Embedding (`B_EMB`) — **optional**

| Model ID | Model | Status |
|----------|-------|--------|
| B_EMB_01 | `microsoft/codebert-base` | **Optional** — HF download |
| B_EMB_02 | `microsoft/graphcodebert-base` | Optional |
| B_EMB_03 | `microsoft/unixcoder-base` | Optional |
| B_EMB_04 | `bigcode/starencoder` | Optional |

**Frozen primary embedding (if feasible):** `B_EMB_03` UniXcoder — 768-d mean-pooled last hidden state of `[CLS]` sequence from source only.

**Fallback:** If download fails in CI/offline, `z_EMB(π) = 0⃗` with `embedding_available=false` logged; primary comparison uses **B_NOPROC** without embedding (see §4).

### Family F6 — Trivial / identity (`B_TRIV`)

| ID | Feature | Use |
|----|---------|-----|
| B_TRIV_01 | `majority_class_score` | constant predictor (evaluation only) |
| B_TRIV_02 | `random_score` | seeded uniform (evaluation only) |
| B_TRIV_03 | `problem_id_onehot` | problem identity (nuisance) |
| B_TRIV_04 | `model_id_onehot` | model identity (LLM stratum) |

Not used in primary models B/D except as **diagnostic** rows in ablation table.

### Family B_IO — Public-test-only conductual (`B_IO`)

**Primary baseline A.** Equals **P1 model vector** from EPS spec:

```
z_IO(π) = P1_model(π) ∈ ℝ^{m·8}
```

Uses **only** public test outputs. **No** execution process beyond I/O capture required for P1.

---

## 3. Combined non-process baseline (`B_NOPROC`)

**Primary baseline B** — concatenation of **mandatory** non-process families:

```
z_NOPROC(π) = z_IO(π) ⊕ z_SIZE(π) ⊕ z_AST(π) ⊕ z_TOK(π) ⊕ z_BC(π) ⊕ [ z_EMB(π) if embedding_available ]
```

**Frozen mandatory components:** IO, SIZE, AST, TOK, BC.  
**Optional component:** EMB (included in **B_full**; excluded in **B_noemb** ablation).

Standardization: development corpus only (`μ, σ` per scalar dimension).

---

## 4. Primary comparison models (frozen)

| Model ID | Name | Feature vector | Role |
|----------|------|----------------|------|
| **M_A** | Public I/O only | `z_IO` | Baseline **A** — conductual floor |
| **M_B** | Non-process combined | `z_NOPROC` | Baseline **B** — **primary syntactic/structural competitor** |
| **M_C** | EPS only | `EPS_proc = (P2,…,P7)` | Process without I/O (diagnostic) |
| **M_D** | Non-process + EPS | `z_NOPROC ⊕ EPS(π)` | **Primary success model** |

**Primary statistical comparison (holdout):**

```
Δ_AUC_primary = AUC(M_D) - AUC(M_B)
Δ_AUPRC_primary = AUPRC(M_D) - AUPRC(M_B)
```

**Secondary (reported, not success gate):**

```
Δ_AUC_IO = AUC(M_D) - AUC(M_A)
Δ_AUC_EPS_only = AUC(M_C) - AUC(M_B)
```

### 4.1 Primary success criterion (frozen)

**Success** on holdout iff **all**:

1. `Δ_AUC_primary ≥ 0.05` **OR** (`prevalence(y) < 0.10` AND `Δ_AUPRC_primary ≥ 0.05`)  
2. Effect direction consistent (M_D > M_B) in **≥ 1** preregistered stratum (checker / difficulty / source)  
3. EPS dimensions remain interpretable (no single opaque fused embedding as **only** EPS component)  
4. Leakage audit pass (§6)

**Failure:** `Δ_AUC_primary < 0.05` and `Δ_AUPRC_primary < 0.05` → EPS does not add beyond non-process (informative null).

---

## 5. Estimator and test (frozen)

- **Classifier:** L2-regularized logistic regression (`C=1.0` frozen; no hyperparameter search on holdout)  
- **Training:** PRIMARY_DEVELOPMENT public-pass population only  
- **Evaluation:** HOLDOUT_PRIMARY public-pass only  
- **Inference:** cluster bootstrap by `problem_id`, B=2000  
- **Test:** one-sided superiority M_D vs M_B at α=0.05 on Δ_AUC (DeLong or bootstrap CI lower bound > 0 for success margin)

**Forbidden:** training on holdout; feature selection on holdout; dropping baseline families post hoc.

---

## 6. Leakage controls

| Control | Mechanism |
|---------|-----------|
| LC-01 | Extractors accept only `(π, public_run_records)` |
| LC-02 | `LabelBuilder` separate module; labels never passed to `BaselineExtractor` / `EPSExtractor` |
| LC-03 | `z_NOPROC` vocab / hash sketches fit on development only |
| LC-04 | P6 pool medians development-only (EPS spec) |
| LC-05 | Unit test asserts extractors reject kwargs `withheld_*`, `label`, `y` |
| LC-06 | Static audit: no `import invert` / `invert_core` in `latent_process_risk` |

---

## 7. Per-baseline attribute matrix

See `baseline_features.csv` for full table (motivation, leakage, cost, reviewer value).

---

## 8. Prohibited changes after lock

- Removing AST or token baselines after seeing ΔAUC  
- Adding syntax features correlated with holdout failures only  
- Using withheld outputs in any baseline  
- Using LLM judges for algorithm labels  
- Tuning embedding model choice on holdout  

---

## 9. Document history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-29 | Initial frozen baseline protocol |

---

*End of baseline specification.*
