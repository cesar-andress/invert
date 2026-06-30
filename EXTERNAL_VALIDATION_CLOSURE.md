# External Validation Branch — Closure Record

**Date:** 2026-06-30  
**Status:** Closed for current INVERT submission  
**Scope:** Feasibility probes only; not confirmatory results

No frozen detector source, frozen generalization run, or confirmatory CSV was modified during these probes.

---

## Scientific conclusion

The current INVERT dynamic detectors recover process signatures **relative to the INVERT harness contract**, not as interface-agnostic measures of process intent on arbitrary code.

| Class | Frozen detector | Required contract | External applicability (frozen) |
|-------|-----------------|-------------------|--------------------------------|
| D | `bfs_dfs.py` | `GraphTraversal(graph, start, visit_fn)`, `reachable_nodes()`, `BfsDfsTask` graphs | **No** — abstains on competitive-programming code |
| E | `deterministic_randomized.py` | `ItemProcessor(items, visit_fn, seed=None)`, `process_all()`, `DeterministicRandomizedTask` oracle | **No** — abstains on arbitrary Python / stdin–stdout code |

Both detectors classify correctly on INVERT-conformant archived artifacts. Both abstain or fail to classify external code that does not expose the required trace surface.

**Confirmatory external validation is out of scope for this submission.** A future study would require a **new preregistered detector or trace-extraction layer** defined and frozen before external evaluation—not a post-hoc adapter that wraps foreign code into INVERT APIs.

---

## Class D — EffiBench-X feasibility (48h)

**Files:** `EXTERNAL_EFFIBENCH_FEASIBILITY.md`, `external_effibench_go_no_go.json`, `external_effibench_candidate_tasks.csv`

| Field | Value |
|-------|-------|
| Recommendation | `revise-plan` (not `go`) |
| Frozen detector SHA256 (`bfs_dfs.py`) | `10fecb7e623913d63cc69047f041d526d8dfb0e3b5f6db015102228d72d05671` |
| Detector modified | No |
| Main blocker | Native EffiBench-X Python solutions use `class Solution` / stdin–stdout, not `GraphTraversal` + `visit_fn` |
| Prototype outcome | `ambiguous` (`no_graph_traversal_class`) on canonical tree task |

EffiBench-X remains useful as an efficiency benchmark and problem source, but not as a drop-in host for the frozen Class D detector.

---

## Class E — external smoke feasibility (1 day)

**Files:** `EXTERNAL_CLASS_E_FEASIBILITY.md`, `external_class_e_go_no_go.json`, `external_class_e_smoke_results.csv`

| Field | Value |
|-------|-------|
| Recommendation | `no-go` |
| Frozen detector SHA256 (`deterministic_randomized.py`) | `ab5e5a91750dbd17c0e87e6bd8338db1fd92ac2fce7c244e3b02c31fbc3e5f23` |
| Detector modified | No |
| Main blocker | Detector requires `ItemProcessor` + `visit_fn` visit traces and `expected_items` oracle; arbitrary functions and EffiBench-X solutions do not satisfy the contract |
| Positive controls | Frozen INVERT artifacts and synthetic conforming wrappers classify as expected |

Repeated execution alone does not remove trace-contract dependence: Class E classifies **visit-trace identity** under the harness, not raw stdout variability across subprocess runs.

---

## Why adapters and wrappers were rejected

Wrapping external code in `GraphTraversal` or `ItemProcessor` would:

1. Define what counts as a visit trace (construct-validity risk: **high**).
2. Reintroduce detector–task co-design through the adapter layer.
3. Violate the frozen-detector discipline for external validation.

Pure repeated subprocess execution with output comparison is **not** what the frozen Class E detector implements.

---

## What future interface-agnostic detection would require

1. **Preregister** an extraction layer (e.g., repeated-run stdout hashes, profiling events, or syscall traces) **before** seeing external corpora.
2. **Freeze** that layer and any classification rules derived from it.
3. **Evaluate** on independent corpora under a separate protocol—without retrofitting INVERT harness APIs onto foreign code.
4. Estimated effort for a defensible external study with new tooling: **21+ days** per dimension (not feasible within the current submission window).

---

## Paper and artifact alignment

- Main paper: trace-contract dependence threat (Classes D and E); external corpora marked out of scope; no EffiBench-X empirical claims.
- This file and sibling feasibility notes are **exploratory documentation**, not confirmatory results.
- See also `REVIEW_LIMITATIONS.md` for experiment backlog items deferred past submission.
