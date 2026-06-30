# External Process Signature (EPS): Instrument Specification

**Study ID:** `LPR-2026-001`  
**Document:** `EPS_SPECIFICATION.md`  
**Version:** 1.0  
**Status:** FROZEN — specification only; no implementation exists at lock time  
**Date:** 2026-06-29  
**Repository:** `cesar-andress/invert`  
**Protocol lock (dataset):** `ff450096985b22273dd0b75d011f493cc925d41b`  
**Companion artifacts:** `eps_features.csv`, `eps_ablation_plan.md`, `eps_go_no_go.json`

---

## 0. Instrument charter

The **External Process Signature (EPS)** is a scientific instrument that maps an executable program, together with a **public test suite**, to a **finite-dimensional feature vector** characterizing **observable execution process**—timing, resources, stability, and low-level execution structure—**without** access to withheld tests, outcome labels, prompt text, benchmark-specific hooks, or INVERT instrumentation.

EPS is **not** a detector, classifier, or correctness oracle. It is a **measurement protocol** whose outputs may later be used as predictors in LPR analyses defined in `PREREGISTRATION.md`.

### 0.1 Independence from INVERT

EPS **must not** use:

| Forbidden | Reason |
|-----------|--------|
| `GraphTraversal`, `ItemProcessor`, `visit_fn` | INVERT-specific adapters |
| INVERT detectors or pole labels | Outcome of recovery, not execution |
| Benchmark-specific APIs injected into user code | Violates ordinary execution |
| Prompt metadata | Not observable at run time |
| Withheld test inputs/outputs | Label leakage |
| Latent-incorrectness or pass/fail labels | Label leakage |

EPS **may** use only information produced by **ordinary execution** of program `π` on **public test inputs** under the frozen sandbox in `corpus_filters.yaml`.

### 0.2 Alignment with preregistered dimensions

The frozen EPS instrument exposes exactly **seven** scalar/vector **dimensions** with locked names `P1`–`P7` (see §8). Names match `PREREGISTRATION.md`; operational definitions are completed here.

---

## 1. Mathematical preliminaries

### 1.1 Objects

| Symbol | Type | Definition |
|--------|------|------------|
| `π` | Program | Source string + entry point resolved by public harness only |
| `𝒯_pub` | Finite set | Public test cases `{t₁,…,t_m}` indexed by frozen `split_rule.yaml` |
| `m` | ℕ | `|𝒯_pub|`; preregistered minimum ≥ 20 |
| `R` | ℕ | **Repeat count** for stability probes; **frozen** `R = 3` |
| `ℰ` | Sandbox | Frozen execution environment (Python 3.10, limits in `corpus_filters.yaml`) |
| `Execute` | Partial function | `Execute(π, t, r) → RunRecord` or `⊥` (timeout/error) |

A **run** is indexed by `(π, t, r)` where `r ∈ {1,…,R}`.

### 1.2 Execution Event

An **execution event** is an atomic observable record emitted by the sandbox instrumentation at run time:

```
e = (κ, τ, δ)
```

where:

- `κ ∈ 𝒦` — **event kind** from a frozen enumeration (§4.1)  
- `τ ∈ ℝ≥0` — **monotonic wall-clock offset** (seconds from run start)  
- `δ` — **kind-specific payload** (JSON-serializable, bounded size)

Examples of `κ`: `opcode`, `call_return`, `line`, `memory_sample`, `io_write`, `exception`, `run_start`, `run_end`.

**Constraint:** Events must not include withheld-test data, prompt fields, or INVERT trace contracts.

### 1.3 Process Observation

A **process observation** is the **multiset** (or time-ordered sequence) of execution events from one successful run:

```
O(π, t, r) = (e₁, e₂, …, e_n)   if Execute(π,t,r) succeeds
             = ⊥                 otherwise
```

Let `𝒪(π) = { O(π,t,r) : t ∈ 𝒯_pub, r ∈ {1,…,R}, O(π,t,r) ≠ ⊥ }`.

**Extraction population:** EPS is defined for programs that **pass all public tests** (LPR analysis population). For failed runs, instrument returns `⊥` (excluded from analysis per preregistration).

### 1.4 Feature map and feature vector

A **feature** is a measurable function:

```
f_k : 𝒪(π) → ℝ^{d_k}
```

The **raw feature vector** is concatenation over frozen features:

```
F_raw(π) = ⨁_{k=1}^{K} f_k(𝒪(π))  ∈ ℝ^D
```

where `⨁` denotes vector concatenation and `D = Σ_k d_k`.

### 1.5 Aggregation

**Aggregation** maps event-level observations to per-run or per-program statistics.

| Level | Symbol | Definition |
|-------|--------|------------|
| Per-run | `Agg_run` | Maps `O(π,t,r)` → vector `u ∈ ℝ^p` (e.g., opcode histogram for one run) |
| Per-test | `Agg_test` | Maps `{O(π,t,r)}_{r=1}^R` → vector `v ∈ ℝ^q` (e.g., stability across repeats) |
| Per-program | `Agg_prog` | Maps `{Agg_test(π,t)}_{t∈𝒯_pub}` → dimension `P_i` |

All aggregators are **fixed functions** declared in §8; no data-driven learning of aggregators on holdout labels.

### 1.6 Normalization

**Development-frozen normalization:** For each scalar component `j` of `F_raw`:

```
F_norm[j] = (F_raw[j] - μ_j) / σ_j
```

where `(μ_j, σ_j)` are computed **only** on the LPR **PRIMARY_DEVELOPMENT** corpus, public-pass programs, and **frozen** before holdout evaluation. If `σ_j = 0`, set `F_norm[j] = 0`.

**Per-dimension alternative (P4, P7):** Probability mass functions (PMFs) are **ℓ₁-normalized** to sum 1 before distance computations.

**Hash outputs (P1):** Normalized to fixed-length hex strings; no z-scoring.

### 1.7 Distance

For vectors `x, y ∈ ℝ^d`:

**L2 distance:**
```
d₂(x,y) = ‖x - y‖₂
```

For discrete distributions `p, q` over finite support `𝒮`:

**Jensen–Shannon divergence:**
```
JSD(p,q) = ½ KL(p‖m) + ½ KL(q‖m),   m = ½(p+q)
```

with base-2 logarithm; report `√JSD` when a metric is required.

For hash strings `h₁, h₂`:

**Equality distance:**
```
d_H(h₁,h₂) = 0  if h₁ = h₂;  1 otherwise
```

### 1.8 Similarity

**Similarity** is a declared transformation of distance:

```
sim(x,y) = exp(-λ · d(x,y))   or   sim(p,q) = 1 - √JSD(p,q)
```

Frozen uses:

| Context | Similarity |
|---------|------------|
| PMF opcode profiles | `sim_opcode(p,q) = 1 - √JSD(p,q)` |
| Normalized resource vectors | `sim_res(x,y) = exp(-d₂(x,y))` |
| Output hashes | `sim_out = 1 - d_H` |

### 1.9 External Process Signature (EPS)

The **External Process Signature** is the **named 7-tuple** of preregistered dimensions:

```
EPS(π) = (P1(π), P2(π), P3(π), P4(π), P5(π), P6(π), P7(π))
```

where each `P_i(π)` is a **computable functional** of `𝒪(π)` and, for `P6` only, of **frozen pool statistics** from development (§8.6).

**Process-only subsignature** (for ablations):

```
EPS_proc(π) = (P2, P3, P4, P5, P7)(π)
```

`P1` is the **public I/O baseline** (conductual, not process); retained in full EPS for preregistered models.

---

## 2. Observation protocol (frozen)

### 2.1 Sandbox and repeats

- Python **3.10**, `PYTHONHASHSEED=0`  
- Per-test timeout **30 s**; per-program aggregate **600 s** (`corpus_filters.yaml`)  
- **R = 3** identical re-executions per `(π, t)` with **same** `t` and **no** injected RNG seeding  
- Memory peak via `resource.getrusage` or `/proc/self/status` VmHWM — **one** frozen backend selected at implementation time; not tuned to outcomes  

### 2.2 Instrumentation modes (frozen stack)

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| L0 | Wall/cpu timing, RSS | P4 |
| L1 | `sys.setprofile` call/return counts | P3 auxiliary |
| L2 | `sys.settrace` line events → **opcode category** via `dis` on executing frame | P3, P7 |
| L3 | stdout/stderr capture | P1, P2 |

**Explicitly excluded:** `visit_fn`, graph adapters, bytecode rewriting, AST injection.

### 2.3 Event kind enumeration `𝒦` (frozen)

```
run_start, run_end, opcode_cat, call_enter, call_return,
memory_sample, io_stdout_write, exception_raised
```

`opcode_cat` maps CPython 3.10 opcode names to **frozen category table** `𝒞` (§8.7), size `|𝒞| = 32`.

---

## 3. Literature basis (instrument design)

EPS draws on **dynamic software analysis**, **performance profiling**, and **runtime characterization**—not on LLM benchmarks:

| Tradition | Relevance to EPS |
|-----------|------------------|
| Dynamic analysis / execution traces (Ball, Beschastnikh) | Event streams, aggregation |
| Statistical profiling (CPU samples, call counts) | Resource and structure features |
| Opcode / instruction mix (embedded systems, Rajput et al. 2025 DCTD) | P7; comparable but EPS uses category PMF, not claim overlap |
| Software metrics (complexity, Halstead) | **Rejected** as static unless execution-derived |
| Metamorphic / stability testing | Motivates P2, P3 |
| Process mining | **Rejected** for v1 (control-flow graphs from logs — high cost, adapter risk) |

Literature motivates **candidates**; inclusion is decided by robustness and leakage rules (see `eps_features.csv`).

---

## 4. Dimension definitions (frozen operationalization)

### 4.1 P1 — `public_io_signature` (baseline conductual component)

For each `t_j ∈ 𝒯_pub`, single run `r=1`, obtain normalized output string `out(π,t_j)` per harness comparator (exact match unless checker specified on public suite only).

```
P1(π) = ( H(out(π,t_1)), …, H(out(π,t_m)) )
```

`H` = SHA-256 over UTF-8 NFKC-normalized output bytes.

**Type:** vector of hashes; for modeling, map to fixed embedding via **frozen** hash-to-bin function `φ_H` (development-fit **only** on PRIMARY_DEVELOPMENT):

```
P1_model(π) = ( φ_H(H₁), …, φ_H(H_m) ) ∈ ℝ^{m·b},   b = 8 bins frozen
```

### 4.2 P2 — `cross_run_output_stability`

For each `t_j`, runs `r = 1..R`:

```
σ_out(j) = (1/R) Σ_r d_H( H(out(π,t_j,r)), mode_r H(out(π,t_j,r)) )
```

Program-level:

```
P2(π) = (1/m) Σ_j σ_out(j)  ∈ [0,1]
```

**Interpretation:** Low = stable outputs across repeats; high = flaky I/O despite public pass.

### 4.3 P3 — `cross_run_trace_stability`

For each run, opcode-category histogram `p_{j,r} ∈ Δ^{|𝒞|-1}` from L2 trace.

For each `t_j`:

```
JSD_stab(j) = (2 / R(R-1)) Σ_{r<r'} √JSD(p_{j,r}, p_{j,r'})
```

```
P3(π) = (1/m) Σ_j JSD_stab(j)
```

### 4.4 P4 — `resource_profile_dispersion`

Per run `(j,r)`, measure vector:

```
u_{j,r} = ( wall_{j,r}, cpu_{j,r}, rss_peak_{j,r} ) ∈ ℝ³
```

Per test `t_j`, aggregate repeats: `ū_j = median_r u_{j,r}`.

Stack `ū_j` into matrix `U(π) ∈ ℝ^{m×3}`. Column-wise coefficient of variation:

```
P4(π) = ( CV(wall), CV(cpu), CV(rss) ) ∈ ℝ³
```

where `CV(col) = std(col) / (mean(col) + ε)`, `ε = 10⁻⁹`.

### 4.5 P5 — `cross_input_signature_entropy`

Define per-test **micro-signature**:

```
s(π,t_j) = H( concat( hex(p_{j,1}), wall_{j,1}, rss_{j,1} ) )
```

Empirical PMF `q` over `m` bins `{s(π,t_j)}`. Shannon entropy:

```
P5(π) = H₂(q) = - Σ_s q(s) log₂ q(s)
```

### 4.6 P6 — `local_pool_stereotypy`

**Pool bucket** `B = (problem_id, source_stratum, model_id)` (model_id = `NA` for human/mined).

On **PRIMARY_DEVELOPMENT only**, compute frozen reference:

```
μ_B = median{ EPS_proc(π') : π' ∈ public_pass(B), π' ≠ π }
```

(process subsignature excluding P1 and P6 to avoid circularity)

```
P6(π) = d₂( Z(EPS_proc(π)), Z(μ_B) )
```

`Z` = development-frozen normalization of `EPS_proc` components.

**Holdout:** use **only** `μ_B` exported from development; **never** recompute medians on holdout.

### 4.7 P7 — `opcode_profile_signature`

Aggregate opcode-category counts across all public runs and tests:

```
p(π) = (1 / Σ n_c) · (n_1, …, n_{|𝒞|})  ∈ Δ^{|𝒞|-1}
```

Store as **frozen** vector representation `P7(π) = p(π)` (32 dims).

---

## 5. Opcode category table `𝒞` (frozen, |𝒞|=32)

Categories group CPython 3.10 opcodes by **semantic class** (implementation maps via static table; not learned):

`LOAD, STORE, BINARY, COMPARE, BRANCH, CALL, RETURN, BUILD, ATTR, SUBSCR, IMPORT, JUMP, LOOP, EXCEPT, YIELD, ASYNC, FORMAT, DELETE, NOP, CACHE, OTHER` — expanded to **32** fixed slots in implementation artifact `opcode_categories_v1.json` (to be generated at implementation lock; categories **fixed by name** in `eps_go_no_go.json`).

*Specification lock:* exact opcode→category map is **versioned** with EPS v1.0; changes require EPS v2.0 OSF amendment.

---

## 6. Instrument outputs and manifest

For each program `π`:

```json
{
  "program_id": "...",
  "eps_version": "1.0",
  "dimensions": {
    "P1": "...",
    "P2": 0.0,
    "P3": 0.0,
    "P4": [0.0, 0.0, 0.0],
    "P5": 0.0,
    "P6": 0.0,
    "P7": [ ... 32 probabilities ... ]
  },
  "extraction_status": "ok | timeout | error"
}
```

---

## 7. Prohibited post-lock actions

1. Adding features based on holdout ΔAUC  
2. Tuning opcode categories from label correlation  
3. Using withheld tests in any feature  
4. Using LLM judges or syntax embeddings **inside** EPS (syntax baseline is **outside** EPS per preregistration)  
5. Recomputing `μ_B` on holdout  
6. Changing `R`, timeouts, or `𝒞` without EPS version bump  

---

## 8. Frozen feature set summary

| ID | Name | Dim | Included |
|----|------|-----|----------|
| P1 | public_io_signature | m·b or hash tuple | Yes (baseline) |
| P2 | cross_run_output_stability | 1 | Yes |
| P3 | cross_run_trace_stability | 1 | Yes |
| P4 | resource_profile_dispersion | 3 | Yes |
| P5 | cross_input_signature_entropy | 1 | Yes |
| P6 | local_pool_stereotypy | 1 | Yes |
| P7 | opcode_profile_signature | 32 | Yes |

**Total modeling dimensionality:** `1 + 1 + 1 + 3 + 1 + 1 + 32 + P1_bins` with `P1_model` using `b=8` per test hashed to 8-dim bin count vector (frozen in implementation; **not** learned from holdout).

---

## 9. Auditor checklist

- [ ] No INVERT or adapter references in extraction path  
- [ ] All features computable from public tests only  
- [ ] P6 pool statistics development-only  
- [ ] R=3, timeouts match `corpus_filters.yaml`  
- [ ] `eps_features.csv` documents all rejected candidates  
- [ ] Ablations pre-declared in `eps_ablation_plan.md`  
- [ ] `eps_go_no_go.json` criteria unchanged by pilot outcomes before lock  

---

## 10. Document history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-29 | Initial frozen EPS specification |

---

*End of instrument specification. No implementation or data collection is authorized by this document alone.*
