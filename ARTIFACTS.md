# Artifact Inventory — INVERT Core v2 (v1.0.1)

Repository root: extract or clone this package; all paths below are relative to that root.

---

## Configurations (`configs/`)

| File | Purpose |
|------|---------|
| `models.yaml` | Model aliases, temperatures, provider settings |
| `core_v2_generalization_local_quadrature.yaml` | Class B frozen generalization |
| `core_v2_generalization_local_eager_lazy.yaml` | Class C frozen generalization |
| `core_v2_generalization_local_bfs_dfs.yaml` | Class D frozen generalization |
| `core_v2_generalization_local_deterministic_randomized.yaml` | Class E frozen generalization |
| `core_v2_generalization_local_euler_rk4.yaml` | Class A generalization (not confirmatory in paper) |
| `core_v2_*_pilot_local*.yaml` | Development pilots |
| `pilot.yaml`, `experiment.yaml` | Legacy prototype |

---

## Shell scripts (`scripts/`)

| Script | Run ID produced |
|--------|-----------------|
| `run_core_v2_generalization_local_quadrature_001.sh` | `core_v2_generalization_local_quadrature_001` |
| `run_core_v2_generalization_local_eager_lazy_001.sh` | `core_v2_generalization_local_eager_lazy_001` |
| `run_core_v2_generalization_local_bfs_dfs_001.sh` | `core_v2_generalization_local_bfs_dfs_001` |
| `run_core_v2_generalization_local_deterministic_randomized_001.sh` | `core_v2_generalization_local_deterministic_randomized_001` |
| `run_core_v2_*_pilot*.sh` | Development pilots |
| `smoke_test.py` | Legacy smoke test |
| `run_pilot_001.sh` | Legacy pilot |

---

## Preregistration (`prereg/`)

| File | Contents |
|------|----------|
| `core_v2_tasks.json` | Master task registry |
| `predictions.md` | Preregistered predictions |
| `normalizations.md` | Strip-level definitions |

---

## Task specifications (`data/core_v2/tasks/`)

| File | Dimension |
|------|-----------|
| `euler_rk4_tasks.json` | Class A |
| `quadrature_tasks.json` | Class B |
| `eager_lazy_tasks.json` | Class C |
| `bfs_dfs_tasks.json` | Class D |
| `deterministic_randomized_tasks.json` | Class E |

Task loader modules: `src/invert_core/{ode,quadrature,eager_lazy,bfs_dfs,deterministic_randomized}_tasks.py`

---

## Detectors (`src/invert_core/detectors/`)

| File | Dimension |
|------|-----------|
| `integration.py` | Euler vs RK4 |
| `quadrature.py` | Trapezoidal vs Simpson |
| `eager_lazy.py` | Eager vs lazy |
| `bfs_dfs.py` | BFS vs DFS |
| `deterministic_randomized.py` | Deterministic vs randomized |
| `shuffled_control.py`, `lock_control.py` | Controls |
| `stripping.py` (parent: `src/invert_core/stripping.py`) | Format-normalization transforms |

Frozen metadata writer: `src/invert_core/frozen_detector.py`

---

## Behavioral oracles (`src/invert_core/`)

| Module | Dimension |
|--------|-----------|
| `behavioral.py` | ODE integration (Class A) |
| `quadrature_behavioral.py` | Class B |
| `eager_lazy_behavioral.py` | Class C |
| `bfs_dfs_behavioral.py` | Class D |
| `deterministic_randomized_behavioral.py` | Class E |

---

## Generated code and raw outputs (`data/core_v2/`)

| Subdirectory | Contents |
|--------------|----------|
| `raw/<run_id>/` | Raw LLM JSON responses |
| `code/<run_id>/` | Extracted `.py` implementations |
| `stripped/<run_id>/<level>/` | Strip variants: `raw`, `no_comments`, `renamed`, `no_imports`, `format_normalized` |

**Frozen generalization run IDs:**

- `core_v2_generalization_local_quadrature_001`
- `core_v2_generalization_local_eager_lazy_001`
- `core_v2_generalization_local_bfs_dfs_001`
- `core_v2_generalization_local_deterministic_randomized_001`

---

## Result reports (`results/core_v2/`)

### Cross-run summaries

| File | Description |
|------|-------------|
| `core_v2_decision_report.md` | Cross-run decision dashboard |
| `core_v2_dimension_summary.csv` | Per-dimension aggregates |
| `core_v2_model_dimension_summary.csv` | Model × dimension aggregates |

### Per-run directories (`results/core_v2/runs/<run_id>/`)

Typical files per dimension:

| Pattern | Example run |
|---------|-------------|
| `*_detection.csv`, `*_summary.csv`, `*_valid_only_summary.csv`, `*_report.md` | All generalization runs |
| `frozen_detector_metadata.json` | All four frozen generalization runs |
| `eager_lazy_pole_asymmetry.{md,csv}` | Class C only |
| `eager_lazy_full_demand_control.csv` | Class C |
| `deterministic_randomized_fixed_seed_control.csv` | Class E |
| `metadata.json` | Generation metadata |

---

## Frozen detector metadata (`frozen_detector_metadata.json`)

All four frozen generalization runs contain this file. Documented SHA256 hashes (do not modify):

### Shared across runs

| File | SHA256 |
|------|--------|
| `integration.py` | `a251c3ad13ebcd9555757119808997e8c4acb2aa06b7a05043cbaf631cdd5e2c` |
| `quadrature.py` | `c446cbd2ec945cd68cc4e6024d16ad3fb2d0705b424671d73901aba3fe5947a9` |
| `eager_lazy.py` | `1c1abd2bd8816324bf029a7ae06dd36b4e542144dbdab037d083b46ae48aea6b` |
| `bfs_dfs.py` | `10fecb7e623913d63cc69047f041d526d8dfb0e3b5f6db015102228d72d05671` |
| `deterministic_randomized.py` | `ab5e5a91750dbd17c0e87e6bd8338db1fd92ac2fce7c244e3b02c31fbc3e5f23` |

### Per-run `stripping.py` (where present)

| Run | SHA256 |
|-----|--------|
| `core_v2_generalization_local_bfs_dfs_001` | `5032952fceaf4c6b36e78b3f4414a0df1658d4abb37c53692d88356c82b310e0` |
| `core_v2_generalization_local_deterministic_randomized_001` | `aace1f27a9199db78266694f63266c57a782851c4e31fa6126150ad6f338a18b` |

**Note:** `core_v2_generalization_local_eager_lazy_001` metadata does **not** include `stripping.py` (archived artifact state at analysis time). Class B quadrature metadata includes only `integration.py` and `quadrature.py`.

### Git commits recorded at freeze time

| Run | `git_commit` |
|-----|--------------|
| quadrature | `a26c809e4716933e0a7e4db9bc6398e4e6d03294` |
| eager/lazy | `3f8a92d4d16f8b433afb79c57cb73fe4279baccf` |
| bfs/dfs | `646b1af67ed965d561b67591c06402669790727a` |
| deterministic/randomized | `6a1e0afbb0acb694fde21e7195b1f4e6c77082aa` |

---

## Analysis and audit modules

| Module | Role |
|--------|------|
| `src/invert_core/analyze_run.py` | Per-run detector + oracle pipeline |
| `src/invert_core/summarize_core_v2.py` | Cross-run aggregation |
| `src/invert_core/audit_eager_lazy_pole_asymmetry.py` | Class C pole-asymmetry audit |
| `src/invert_core/cli.py` | CLI entry point |

---

## Tests and fixtures

| Path | Contents |
|------|----------|
| `tests/core_v2/` | Pytest modules (~20 files) |
| `tests/core_v2/fixtures/` | Deterministic code fixtures for smoke test |

---

## Legacy prototype (included, not paper focus)

| Path | Contents |
|------|----------|
| `data/intents/tasks.json` | 10 legacy tasks |
| `data/raw/`, `data/code/` (non-core_v2) | Legacy generated artifacts |
| `src/invert/` | Legacy CLI |
| `results/runs/` | Legacy pilot outputs |

---

## External validation feasibility (exploratory, not confirmatory)

The following files document **closed feasibility probes** that informed the paper's trace-contract dependence threat. They are **not** part of the confirmatory artifact set and must not be cited as empirical results:

| File | Contents |
|------|----------|
| `EXTERNAL_VALIDATION_CLOSURE.md` | Summary closure record (Classes D and E) |
| `EXTERNAL_EFFIBENCH_FEASIBILITY.md` | Class D / EffiBench-X probe |
| `external_effibench_go_no_go.json` | Class D go/no-go decision |
| `EXTERNAL_CLASS_E_FEASIBILITY.md` | Class E external smoke probe |
| `external_class_e_go_no_go.json` | Class E go/no-go decision |
| `external_class_e_smoke_results.csv` | Class E smoke outcomes |

No detector or frozen run was modified. Confirmatory evidence remains the four `core_v2_generalization_local_*_001` runs only.

---

## Manuscript (external to this repo)

LaTeX source for the ACM TOSEM manuscript is maintained separately from this replication package (see paper Data Availability; Zenodo DOI assigned on deposit).
