# LPR Baseline Ablation Plan (Frozen)

**Study ID:** `LPR-2026-001`  
**Version:** 1.0  
**Date:** 2026-06-29  
**Authority:** `BASELINE_SPECIFICATION.md`, `PREREGISTRATION.md`

---

## 1. Purpose

Pre-declare **baseline model variants** for secondary analysis. **Primary confirmatory** comparison remains **M_D vs M_B** (§4 `BASELINE_SPECIFICATION.md`).

---

## 2. Frozen model variants

| ID | Model | Feature set | Question |
|----|-------|-------------|----------|
| **BL-0** | M_A | `z_IO` | Conductual floor |
| **BL-1** | M_B | `z_NOPROC` full | **Primary competitor** |
| **BL-2** | M_C | `EPS_proc` (P2–P7) | Process without syntax |
| **BL-3** | M_D | `z_NOPROC ⊕ EPS` | **Primary success** |
| **BL-4** | M_B_noemb | `z_NOPROC` without `z_EMB` | Syntax without neural |
| **BL-5** | M_D_noemb | BL-4 + EPS | Success without embedding |
| **BL-6** | M_B_size | `z_IO ⊕ z_SIZE` | Minimal surface |
| **BL-7** | M_B_ast | `z_IO ⊕ z_AST` | AST-only augment |
| **BL-8** | M_B_tok | `z_IO ⊕ z_TOK` | Token-only augment |
| **BL-9** | M_B_bc | `z_IO ⊕ z_BC` | Static bytecode only |
| **BL-10** | M_B_emb | `z_IO ⊕ z_EMB` | Embedding-only augment |

---

## 3. Execution schedule (later)

| Phase | Models | Corpus |
|-------|--------|--------|
| Confirmatory primary | BL-1 vs BL-3 | Holdout |
| Secondary dissociation | BL-3 vs BL-4, BL-5 | Holdout |
| Family attribution | BL-3 vs BL-6…BL-10 | Development + Holdout report |
| Trivial diagnostics | B_TRIV_* | Holdout appendix |

**Forbidden:** selecting BL-10 as primary post hoc because it beats BL-3 on development.

---

## 4. Interpretation rules

| Outcome | Meaning |
|---------|---------|
| BL-3 > BL-1 | EPS adds beyond frozen non-process bundle |
| BL-3 ≈ BL-1, BL-2 > BL-1 | Process signal exists but redundant with syntax bundle |
| BL-5 ≈ BL-3 | Embedding unnecessary for margin |
| BL-8 ≈ BL-1 | Token baseline subsumes reported EPS gain (reviewer attack) |

---

## 5. Document history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-29 | Initial freeze |
