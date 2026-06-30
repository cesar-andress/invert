# External Class E Feasibility — 1-Day Smoke Study

**Date:** 2026-06-30  
**Scope:** Class E (deterministic vs randomized / inter-execution variability) external applicability  
**Constraints:** Frozen detector unchanged (SHA256 `ab5e5a91750dbd17c0e87e6bd8338db1fd92ac2fce7c244e3b02c31fbc3e5f23`); no detector tuning; no modification of frozen generalization runs; no paper edits.

---

## Executive recommendation

**Go/no-go:** `no-go`

Class E does **not** escape the INVERT trace-contract problem. The frozen `deterministic_randomized` detector runs unchanged but is **not applicable** to arbitrary executable Python or native EffiBench-X solutions. It requires the INVERT `ItemProcessor` harness API, a `visit_fn` callback trace surface, and a `DeterministicRandomizedTask` items oracle.

Repeated execution alone is insufficient: the detector never observes stdout-only or free-function programs unless they are wrapped in the INVERT contract.

---

## 1. Frozen detector contract (unchanged)

**File:** `src/invert_core/detectors/deterministic_randomized.py`  
**SHA256:** `ab5e5a91750dbd17c0e87e6bd8338db1fd92ac2fce7c244e3b02c31fbc3e5f23`

| Requirement | Detail |
|---------------|--------|
| Required class | `ItemProcessor` |
| Constructor | `ItemProcessor(items, visit_fn, seed=None)` |
| Required method | `process_all()` returning a set/list coercible to `task.expected_items` |
| Trace collection | `visit_fn(item)` invoked during `process_all`; visit order forms the trace |
| Task input | `DeterministicRandomizedTask` from `deterministic_randomized_tasks.json` |
| Repeated runs | 5 executions (`DEFAULT_RUN_COUNT`); primary mode uses `seed=None` |
| Classification | `unique_trace_count == 1` → deterministic; `>= 2` → randomized; else ambiguous |
| Output validation | `process_all()` output set must match `task.expected_items` or → ambiguous |

The detector does **not** compare raw stdout across runs, wall-clock timing, or arbitrary side effects. It classifies **visit-trace identity** under the harness.

---

## 2. Smoke-test matrix

See `external_class_e_smoke_results.csv`.

| Case | Source | Result | Reason |
|------|--------|--------|--------|
| `arbitrary_deterministic_function` | local smoke (`def solve`) | **ambiguous** | `no_item_processor_class` |
| `arbitrary_randomized_function` | local smoke (`random.shuffle`) | **ambiguous** | `no_item_processor_class` |
| `synthetic_conforming_deterministic` | local smoke (INVERT API) | **deterministic** | `identical_traces_across_runs` |
| `synthetic_conforming_randomized` | local smoke (INVERT API) | **randomized** | `variable_traces_across_runs` |
| `frozen_invert_deterministic_rep1` | archived artifact | **deterministic** | `identical_traces_across_runs` |
| `frozen_invert_randomized_rep1` | archived artifact | **randomized** | `variable_traces_across_runs` |
| `effibench_x_yokohama-phenomena` | HF `EffiBench/effibench-x` | **ambiguous** | `exec_failed` (stdin/stdout program) |
| `effibench_x_nested-repetition-compression` | EffiBench-X | **ambiguous** | `exec_failed` |
| `effibench_x_chayas` | EffiBench-X | **ambiguous** | `exec_failed` |

**Positive controls:** frozen INVERT artifacts and synthetic conforming wrappers behave as expected.  
**Arbitrary Python:** abstains before execution.  
**EffiBench-X:** code loads but fails under detector `exec`/instantiation because solutions are competitive-programming programs, not `ItemProcessor` implementations.

---

## 3. Adapter analysis

A hypothetical adapter could wrap external code in `ItemProcessor` and call `visit_fn` on extracted events. That adapter would **define what counts as a visit trace** and would need task-specific item lists and output oracles (`expected_items`).

Under the study constraints:

- **Not externally valid** — high construct-validity risk (`adapter_construct_validity_risk: high`).
- **Reintroduces detector-task co-design** through the wrapper, analogous to the Class D EffiBench-X finding.
- **Not allowed** for this feasibility check without violating “no adapter may impose a new process signature.”

Pure repeated subprocess execution with stdout comparison is **not** what the frozen detector implements.

---

## 4. Comparison to Class D EffiBench-X finding

| Aspect | Class D | Class E |
|--------|---------|---------|
| Repeated execution | No (single-run visit order) | Yes (5 runs) |
| INVERT-specific API | `GraphTraversal` + `visit_fn` | `ItemProcessor` + `visit_fn` |
| Arbitrary Python | No-go | No-go |
| EffiBench-X native code | Abstains / fails | Abstains / fails |
| Escapes trace contract? | **No** | **No** |

The inter-execution variability dimension does **not** remove dependence on the INVERT instrumentation surface.

---

## 5. Effort estimate for a defensible external Class E study

| Component | Estimate |
|-----------|----------|
| Design interface-agnostic trace extractor (new detector generation) | 10–14 days |
| Or build per-benchmark adapters + new generation run | 14–21 days |
| Frozen-detector external study as specified (no new detector) | **Blocked** |

**Estimated effort if pursuing external validation with frozen detector only:** not feasible (`no-go`).  
**Estimated effort for a revised plan with new interface-agnostic tooling:** **21+ days**.

---

## 6. Machine-readable outputs

- `external_class_e_go_no_go.json` — decision record  
- `external_class_e_smoke_results.csv` — per-case detector outcomes  

---

## 7. Recommended next step

1. **Do not** launch an external Class E study with the frozen detector on EffiBench-X or arbitrary Python corpora.  
2. Treat Class E as **trace-contract dependent** in the same construct-validity framing as Class D.  
3. If external variability measurement is desired later, specify a **new** detector generation that observes externally defined repeated-run traces (e.g., stdout hashes or profiling events) under a separate preregistered protocol—not an `ItemProcessor` wrapper around foreign code.
