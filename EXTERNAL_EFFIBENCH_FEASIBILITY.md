# EffiBench-X External Sanity Check — 48h Feasibility Study

**Date:** 2026-06-30  
**Scope:** Class D (BFS vs DFS / traversal order) external validation for INVERT  
**Constraints:** Frozen detector unchanged (SHA256 `10fecb7e623913d63cc69047f041d526d8dfb0e3b5f6db015102228d72d05671`); no detector tuning; no modification of frozen generalization runs.

---

## Executive recommendation

**Go/no-go:** `revise-plan` (not `go` for the stated study design)

The frozen Class D detector **runs without code changes** but is **not applicable** to native EffiBench-X Python solutions. EffiBench is feasible as an **efficiency benchmark** (runtime/memory on competitive-programming tasks) and as a **source of graph/tree problems**, but not as a drop-in host for the existing `GraphTraversal` + `visit_fn` contract without a substantial adapter layer that re-implements INVERT’s synthetic API on extracted graphs.

**Estimated effort for the originally envisioned study (frozen detector on independent open code, order signature predicts runtime/memory):** **21+ days**, likely **4–6 weeks** — exceeds the 2–3 week window.

---

## 1. EffiBench-X installation and smoke test

| Step | Result |
|------|--------|
| Clone `https://github.com/EffiBench/EffiBench-X` | OK (`external_study/EffiBench-X/`) |
| `pip install -r requirements.txt` + `pip install -e .` | OK (`import effibench`) |
| Docker available | OK (`Docker version 29.4.3`) |
| HF dataset `EffiBench/effibench-x` | OK (623 problems; cached locally) |
| Full Docker sandbox `start_sandbox.py` | **Not exercised end-to-end** in this study (not required to establish API mismatch) |
| Local subprocess execution of canonical Python solution | **Partial** — LeetCode-style stubs need wrapper imports (`List`); EffiBench test runners provide this |

**Conclusion:** EffiBench-X **can be installed** and the dataset **can be loaded locally**. Official profiling path expects the EffiBench sandbox (Docker); **precomputed runtime/memory** for human canonical solutions are already in the dataset JSON.

---

## 2. Frozen Class D detector contract (unchanged)

From `src/invert_core/detectors/bfs_dfs.py` (frozen):

1. Python source must define a class (preferably `GraphTraversal`) with `__init__(self, graph, start, visit_fn)` (≥4 init args).
2. A method such as `reachable_nodes()` runs traversal and calls `visit_fn(node)` per visit.
3. `detect_bfs_dfs(code, task)` executes that code on a **`BfsDfsTask`** from `data/core_v2/tasks/bfs_dfs_tasks.json`.
4. Classification compares the observed `visit_trace` to **exact** `expected_bfs_order` / `expected_dfs_order` computed from the task’s adjacency dict (neighbor list order matters).

INVERT archived artifact (positive control):

```
data/core_v2/code/.../branching_1/bfs/rep_1.py  →  detector: bfs (visit_trace_matches_bfs_only)
```

---

## 3. Prototype (1 task end-to-end)

**Task:** `leetcode_3191_maximum-score-after-applying-operations-on-a-tree`  
(tags: `tree`, `depth-first-search`; canonical Python solution uses recursive `dfs` on adjacency lists)

| Step | Outcome |
|------|---------|
| Load canonical solution from HF dataset | OK |
| Run frozen `detect_bfs_dfs(code, branching_1 task)` | **`ambiguous`** — reason: `no_graph_traversal_class` |
| Local subprocess on 1 generated test (raw solution file) | **Fail** — missing `List` import / LeetCode harness |
| Dataset profiling fields for canonical solution | Present (`runtime`, `memory` in `solutions.python3`) |

**Interpretation:** The detector **abstains honestly** on EffiBench-native code. It does **not** read traversal order from arbitrary competitive-programming DFS implementations.

---

## 4. Candidate graph/tree tasks (5 selected)

See `external_effibench_candidate_tasks.csv` (25 ranked; top 5 below).

| task_id | title | tests | profiling | visit trace via frozen detector | risk |
|---------|-------|-------|-----------|--------------------------------|------|
| `leetcode_3517_shortest-distance-after-road-addition-queries-i` | Shortest Distance After Road Addition Queries I | yes | metadata | **No** — no `GraphTraversal` API | high |
| `leetcode_3633_maximize-the-number-of-target-nodes-after-connecting-trees-i` | Maximize the Number of Target Nodes… | yes | metadata | **No** | high |
| `atcoder_abc396d_minimum-xor-path` | D - Minimum XOR Path | yes | metadata | **No** | high |
| `atcoder_abc397e_path-decomposition-of-a-tree` | E - Path Decomposition of a Tree | yes | metadata | **No** | high |
| `leetcode_3191_maximum-score-after-applying-operations-on-a-tree` | Maximum Score After Applying Operations on a Tree | yes | metadata | **No** (prototype verified) | high |

**Pool:** 38 / 623 problems mention graph/tree/traversal in title or description; **0** expose INVERT’s `GraphTraversal` + `visit_fn` interface.

---

## 5. Feasibility answers (core questions)

| # | Question | Answer |
|---|----------|--------|
| 1 | Install and run locally? | **Yes** (repo + dataset + package; Docker for official sandbox) |
| 2 | Small number of Python problems + pass/fail? | **Yes** via `generated_tests` + `evaluator` (needs EffiBench runner/harness) |
| 3 | Runtime/memory automatically? | **Yes** — precomputed in dataset; live measurement via EffiBench evaluate + Docker |
| 4 | Graph/tree tasks where BFS/DFS may emerge? | **Yes** — ≥38 candidates; traversal style not standardized |
| 5 | Instrument visit trace? | **Not without adapter** — solutions do not accept `visit_fn`; would require wrapper code **outside** detector |
| 6 | Frozen detector reads trace without logic change? | **Only on `GraphTraversal` code** — not on EffiBench-native solutions |
| 7 | Avoid BFS/DFS naming in prompts? | **Possible** for new LLM generation, but then you are running a **new** generation study, not auditing EffiBench canonical code |
| 8 | Feasible in 2–3 weeks? | **No** for frozen-detector external validation as originally scoped |
| 9 | Main blocker? | **API / representation mismatch** between EffiBench I/O solutions and INVERT Class D harness |

---

## 6. What would *not* violate constraints (revised plan options)

### Option A — Efficiency-only external study (no frozen Class D on EffiBench code)

- Use EffiBench for **functional pass + runtime/memory** on graph tasks.
- Correlate **INVERT Class D labels on synthetic Family 1 artifacts** with EffiBench efficiency separately.
- Does **not** answer “frozen detector recovers order on external code.”

### Option B — Adapter harness (detector unchanged, new code outside detector)

- Extract graph from EffiBench problem → build `BfsDfsTask` JSON + generate/wrap `GraphTraversal` implementations.
- Run **frozen** `detect_bfs_dfs` on wrapper code only.
- Requires: graph extraction tooling, neutral prompts (no “BFS/DFS”), new LLM generation run, behavioral oracle mapping (reachable set ≠ competitive-programming I/O).
- **Effort:** 4–6 weeks; high construct-validity risk.

### Option C — Stay internal; document EffiBench as future work

- Lowest risk for current submission.

---

## 7. Prompt constraint (BFS/DFS naming)

EffiBench canonical solutions are **not prompt-generated** in this study; tags like `breadth-first-search` appear in LeetCode metadata only.

Any **new** generation for external validation must use neutral wording (“traverse all nodes”, “explore neighbors”) — feasible but constitutes a **separate preregistered run**, not EffiBench canonical replay.

---

## 8. Artifacts produced

| File | Purpose |
|------|---------|
| `EXTERNAL_EFFIBENCH_FEASIBILITY.md` | This report |
| `external_effibench_candidate_tasks.csv` | 25 ranked candidates |
| `external_effibench_go_no_go.json` | Machine-readable decision |
| `external_study/EffiBench-X/` | Cloned upstream repo |
| `external_study/sample_make_it_simple.json` | Sample problem export |

---

## 9. Detector integrity

| Check | Status |
|-------|--------|
| `bfs_dfs.py` modified | **No** |
| Frozen SHA256 changed | **No** |
| Frozen generalization runs modified | **No** |
| Manual annotation used | **No** |

---

## 10. Recommended next step

**Do not** launch a 2–3 week EffiBench external Class D study on the current frozen detector contract.

**If external validation remains a priority:**

1. **Short term (paper):** Cite EffiBench as future work; keep confirmatory claims on frozen Family 1 runs.
2. **Medium term:** Prototype **Option B** on **one** extracted graph with a **separate** `external_effibench_pilot_001` run ID (not mixed with confirmatory tables).
3. **Alternative:** Use EffiBench only for **efficiency correlation** (Option A) without claiming detector transfer.
