# Reproducibility Guide — INVERT Core v2

This document lists exact commands to verify the replication package accompanying the ACM TOSEM manuscript *INVERT: The Process Trinity of Generated Code*.

**Assumptions:** Python ≥ 3.10, editable install (`pip install -e ".[dev]"`), working directory `~/papers/invert/invert`.

**Policy:** Confirmatory paper claims cite **frozen generalization runs** only. Development pilots are documented but not used for confirmatory statistics. The commands below distinguish **verification** (read archived outputs), **analysis replay** (re-run detectors on archived generated code; no LLM calls), and **full regeneration** (requires Ollama; optional).

---

## 1. Environment setup

```bash
cd ~/papers/invert/invert
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## 2. Smoke test (no APIs)

```bash
invert-core smoke-test
```

**Expected:** JSON fixture report with `"passed": true` and stdout ending in `Smoke test passed.`

Legacy prototype (optional):

```bash
python scripts/smoke_test.py
```

---

## 3. Full test suite

```bash
pytest
```

**Expected:** all tests pass (187 tests as of 2026-06-29).

Class C pole-asymmetry audit coverage:

```bash
pytest tests/core_v2/test_audit_eager_lazy_pole_asymmetry.py -v
```

---

## 4. Regenerate cross-run summaries

Recomputes aggregate CSVs and the decision report from completed runs under `results/core_v2/runs/` (read-only with respect to generated code; re-aggregates existing per-run CSVs):

```bash
invert-core summarize-core-v2
```

**Expected outputs:**

- `results/core_v2/core_v2_model_dimension_summary.csv`
- `results/core_v2/core_v2_dimension_summary.csv`
- `results/core_v2/core_v2_decision_report.md`

---

## 5. Frozen generalization runs — analysis replay

These commands re-run **detectors and behavioral oracles** on **archived** generated code. They do **not** call LLM APIs when `data/core_v2/code/<run_id>/` is present.

### Class B positive control (quadrature)

```bash
invert-core analyze-run \
  --run core_v2_generalization_local_quadrature_001 \
  --config configs/core_v2_generalization_local_quadrature.yaml
invert-core summarize-core-v2
```

**Expected per-run outputs:** `results/core_v2/runs/core_v2_generalization_local_quadrature_001/quadrature_report.md`, `frozen_detector_metadata.json`

### Class C (eager/lazy)

```bash
invert-core analyze-run \
  --run core_v2_generalization_local_eager_lazy_001 \
  --config configs/core_v2_generalization_local_eager_lazy.yaml
invert-core summarize-core-v2
```

**Expected per-run outputs:** `eager_lazy_report.md`, `frozen_detector_metadata.json`

### Class D (BFS/DFS)

```bash
invert-core analyze-run \
  --run core_v2_generalization_local_bfs_dfs_001 \
  --config configs/core_v2_generalization_local_bfs_dfs.yaml
invert-core summarize-core-v2
```

**Expected per-run outputs:** `bfs_dfs_report.md`, `frozen_detector_metadata.json`

### Class E (deterministic/randomized)

```bash
invert-core analyze-run \
  --run core_v2_generalization_local_deterministic_randomized_001 \
  --config configs/core_v2_generalization_local_deterministic_randomized.yaml
invert-core summarize-core-v2
```

**Expected per-run outputs:** `deterministic_randomized_report.md`, `frozen_detector_metadata.json`

---

## 6. Class C pole-asymmetry audit

The audit aggregates existing detection CSVs for the frozen eager/lazy run. Regenerate with:

```bash
python -c "
from invert_core.audit_eager_lazy_pole_asymmetry import run_eager_lazy_pole_asymmetry_audit
from invert_core.paths import project_root
r = run_eager_lazy_pole_asymmetry_audit('core_v2_generalization_local_eager_lazy_001', project_root())
print('Wrote', r.md_path)
"
```

**Expected outputs:**

- `results/core_v2/runs/core_v2_generalization_local_eager_lazy_001/eager_lazy_pole_asymmetry.md`
- `results/core_v2/runs/core_v2_generalization_local_eager_lazy_001/eager_lazy_pole_asymmetry.csv`

Or run the dedicated pytest module (also writes/validates when archived data present):

```bash
pytest tests/core_v2/test_audit_eager_lazy_pole_asymmetry.py -v
```

---

## 7. Full regeneration (optional — requires Ollama)

**Warning:** These scripts call local Ollama models and may take substantial time. Archived outputs are included in the package; full regeneration is optional.

```bash
bash scripts/run_core_v2_generalization_local_quadrature_001.sh
bash scripts/run_core_v2_generalization_local_eager_lazy_001.sh
bash scripts/run_core_v2_generalization_local_bfs_dfs_001.sh
bash scripts/run_core_v2_generalization_local_deterministic_randomized_001.sh
```

Each script runs: `check-apis` → `generate --dry-run` → `generate` → `analyze-run` → `summarize-core-v2`.

Models (local Ollama tags): `qwen2.5-coder:14b`, `qwen2.5-coder:32b`, `qwen3-coder:30b`, `devstral:latest` (Class B uses a subset; see each YAML).

---

## 8. Reading final reports

```bash
less results/core_v2/core_v2_decision_report.md
column -s, -t < results/core_v2/core_v2_dimension_summary.csv | less
ls results/core_v2/runs/core_v2_generalization_local_*/frozen_detector_metadata.json
```

---

## 9. Reproduction status table

Status reflects verification on **2026-06-29** against the archived package in this repository. “Verified” means the command completed successfully and expected output files were present or regenerated consistently.

| Claim | Run ID | Command | Expected output file(s) | Status |
|-------|--------|---------|-------------------------|--------|
| Class B positive control | `core_v2_generalization_local_quadrature_001` | `invert-core analyze-run --run core_v2_generalization_local_quadrature_001 --config configs/core_v2_generalization_local_quadrature.yaml` | `results/core_v2/runs/.../quadrature_report.md`, `frozen_detector_metadata.json` | Verified (archived) |
| Class C support | `core_v2_generalization_local_eager_lazy_001` | `invert-core analyze-run --run core_v2_generalization_local_eager_lazy_001 --config configs/core_v2_generalization_local_eager_lazy.yaml` | `.../eager_lazy_report.md`, `frozen_detector_metadata.json` | Verified (archived) |
| Class D support | `core_v2_generalization_local_bfs_dfs_001` | `invert-core analyze-run --run core_v2_generalization_local_bfs_dfs_001 --config configs/core_v2_generalization_local_bfs_dfs.yaml` | `.../bfs_dfs_report.md`, `frozen_detector_metadata.json` | Verified (archived) |
| Class E support | `core_v2_generalization_local_deterministic_randomized_001` | `invert-core analyze-run --run core_v2_generalization_local_deterministic_randomized_001 --config configs/core_v2_generalization_local_deterministic_randomized.yaml` | `.../deterministic_randomized_report.md`, `frozen_detector_metadata.json` | Verified (archived) |
| Class C pole-asymmetry audit | `core_v2_generalization_local_eager_lazy_001` | `python -c "…run_eager_lazy_pole_asymmetry_audit…"` (§6) | `.../eager_lazy_pole_asymmetry.md` | Verified (archived) |
| Cross-run decision report | (all completed runs) | `invert-core summarize-core-v2` | `results/core_v2/core_v2_decision_report.md` | Verified (2026-06-29 run) |
| Detector/oracle integrity | — | `invert-core smoke-test` | stdout `Smoke test passed.` | Verified (2026-06-29 run) |
| Unit/integration tests | — | `pytest` | 187 passed | Verified (2026-06-29 run) |

---

## 10. Frozen detector metadata

Each frozen generalization run directory contains `frozen_detector_metadata.json` with `git_commit`, `detector_files_hash`, and UTC `timestamp`. See `ARTIFACTS.md` and `ZENODO_AUDIT.md` for hash inventory. **Do not edit detector source when verifying archived hashes.**

---

## 11. Manuscript linkage

LaTeX source of truth: `~/papers/invert/paper/`. Data Availability section references this package (TODO: Zenodo DOI).
