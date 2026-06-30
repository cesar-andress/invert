# EPS Ablation Plan (Frozen)

**Study ID:** `LPR-2026-001`  
**EPS version:** 1.0  
**Status:** FROZEN — ablation variants declared before implementation  
**Date:** 2026-06-29  
**Repository:** `cesar-andress/invert`  
**Authority:** `EPS_SPECIFICATION.md`, `PREREGISTRATION.md` (§14.5 per-dimension ablation)

---

## 1. Purpose

Ablation variants test **which components of the instrument** carry incremental predictive information about **latent incorrectness**—not to **select** features post hoc. All variants below are **declared now**; execution occurs only on **PRIMARY_DEVELOPMENT** for exploration and **HOLDOUT_PRIMARY** for **pre-registered** confirmatory comparison of **full vs. named ablations** (secondary analyses; do not redefine primary H1a).

**Primary confirmatory model** remains **Process Risk Model** with **full EPS (P1–P7)** vs **I/O Baseline (P1 only)** per `PREREGISTRATION.md`.

---

## 2. Variant definitions

Let `EPS(π) = (P1,…,P7)` as in `EPS_SPECIFICATION.md`.

| Variant ID | Name | Dimension set | Vector dimension (approx.) | Role |
|------------|------|---------------|----------------------------|------|
| **A0** | I/O Baseline | `{P1}` | `m·b` | Preregistered baseline model |
| **A1** | **Primary EPS (full)** | `{P1,…,P7}` | full | **Primary Process Risk Model** |
| **A2** | Reduced EPS | `{P1, P2, P4, P7}` | reduced | Drop trace stability (P3), entropy (P5), stereotypy (P6) |
| **A3** | Execution-only EPS | `{P1, P3, P4, P7}` | no stability scalars | Drop P2,P5,P6; keep trace+resource+opcode |
| **A4** | Timing-free EPS | `{P1, P2, P3, P5, P6, P7}` | no P4 | Zero or omit P4 CV components |
| **A5** | Memory-free EPS | `{P1, P2, P3, P5, P6, P7}` | P4 with rss dim removed | P4 → `(CV(wall), CV(cpu))` only |
| **A6** | Trace-free EPS | `{P1, P2, P4, P5, P6}` | no P3,P7 | Disable `sys.settrace` / opcode PMF |

### 2.1 A1 — Primary EPS (full)

**Frozen set:** P1–P7 inclusive.  
**Hypothesis role:** Primary Process Risk Model in H1a/H1b.

### 2.2 A2 — Reduced EPS

**Dropped:** P3 (`cross_run_trace_stability`), P5 (`cross_input_signature_entropy`), P6 (`local_pool_stereotypy`).  
**Rationale:** Test whether **lightweight** instrument (output stability + resources + opcode) suffices.  
**Risk if A2 ≈ A1 on holdout:** Trace and pool features redundant.

### 2.3 A3 — Execution-only EPS

**Dropped:** P2, P5, P6 (all **scalar stability/comparative** features not requiring cross-run output comparison beyond traces).  
**Kept:** P3, P4, P7 (execution structure and resources).  
**Rationale:** Separate **pure execution trace** signal from **output-repeat stability**.

### 2.4 A4 — Timing-free EPS

**Modification:** P4 excluded entirely; wall/cpu not used.  
**Rationale:** Test hardware sensitivity of timing; if A4 ≈ A1, timing is not necessary for transportability.

### 2.5 A5 — Memory-free EPS

**Modification:** P4 third component (RSS CV) removed; P4_dim = 2.  
**Rationale:** RSS noisy in containers; test memory necessity.

### 2.6 A6 — Trace-free EPS

**Dropped:** P3, P7; disable trace profiler hooks.  
**Rationale:** Test whether **expensive** tracing is necessary; compares to resource-only + I/O stability path.

---

## 3. Execution plan (later; frozen schedule)

| Phase | Corpus | Variants run | Purpose |
|-------|--------|--------------|---------|
| **Pilot** | Development `n=100` problems | A1, A6 | Feasibility: trace overhead & timeout rate |
| **Secondary** | Development full | A1–A6 | ΔAUC vs A0; **no** feature dropping decision |
| **Confirmatory secondary** | Holdout | **A1 vs A0** (primary); **A1 vs A2,A4,A6** pre-registered | Reported in ablation table only |
| **Forbidden** | Holdout | Cherry-pick best ablation as primary | STOP per preregistration |

### 3.1 Metrics per variant

For each variant `A_k`:

```
ΔAUC_k = AUC(ProcessModel_k) - AUC(A0)
```

Report 95% CI (problem-cluster bootstrap, same as preregistration).

### 3.2 Multiplicity

Ablation comparisons on holdout: **Benjamini–Hochberg** across **5** tests (A2, A3, A4, A5, A6 vs A1). **Does not** adjust primary H1a.

### 3.3 Computational budget multiplier (expected)

| Variant | Relative trace cost vs A1 |
|---------|---------------------------|
| A1 | 1.0× |
| A2 | ~0.7× |
| A3 | ~0.85× |
| A4 | ~0.9× |
| A5 | ~0.95× |
| A6 | ~0.4× |

---

## 4. Decision rules (interpretation only; not GO/NO-GO for study)

| Outcome | Interpretation |
|---------|----------------|
| A1 > A0 and A6 ≈ A1 | Tracing may be redundant; recommend EPS v1.1 trace-free default |
| A1 > A0 and A4 ≈ A1 | Timing hardware-independent path viable |
| A2 ≈ A1 | P3,P5,P6 optional for deployment |
| A1 ≈ A0 | **Null** for process instrument (informative); not ablation failure |

**No variant** may be promoted to **primary** after viewing holdout unless preregistered amendment (not planned).

---

## 5. Prohibited actions

- Adding A7+ variants after holdout  
- Tuning which dimensions to drop based on development ΔAUC then confirming on holdout as primary  
- Using ablation results to **remove** P dimensions from frozen EPS v1.0 manifest retroactively  

---

## 6. Document history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-29 | Initial frozen ablation plan |
