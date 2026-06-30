# Reproducibility Guide — INVERT Core v2 (v1.0.1)

This document lists exact commands to verify the replication package accompanying the ACM TOSEM manuscript *INVERT: Recovering Quantity, Order, and Variability Signatures from Behaviorally Equivalent Generated Code*.

**Assumptions:** Python ≥ 3.10, editable install (`pip install -e ".[dev]"`), working directory set to the repository root (where `pyproject.toml` lives).

**Policy:** Confirmatory paper claims cite **frozen generalization runs** only. Development pilots are documented but not used for confirmatory statistics. The commands below distinguish **verification** (read archived outputs), **analysis replay** (re-run detectors on archived generated code; no LLM calls; may refresh CSVs), and **full regeneration** (requires Ollama; optional).

---

## 0. One-command artifact verification (recommended)

```bash
bash scripts/verify_artifact.sh
```

Runs smoke test, pytest, aggregation, checksum verification against `KEY_OUTPUTS.sha256`, and paper figure export. **Does not call LLM APIs or Ollama.** See `PAPER_ARTIFACTS.md` for manuscript mapping.

Optional: `INVERT_VERIFY_REPLAY=1 bash scripts/verify_artifact.sh` re-runs `analyze-run` on frozen code (may refresh CSVs if detector sources differ from freeze-time commits; not the default v1.0.1 check).

---

## 1. Environment setup

```bash
cd /path/to/invert
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

**Run ID:** `core_v2_generalization_local_quadrature_001`

```bash
invert-core analyze-run \
  --run core_v2_generalization_local_quadrature_001 \
  --config configs/core_v2_generalization_local_quadrature.yaml
invert-core summarize-core-v2
```

**Expected per-run outputs:** `results/core_v2/runs/core_v2_generalization_local_quadrature_001/quadrature_report.md`, `frozen_detector_metadata.json`

### Class C (eager/lazy)

**Run ID:** `core_v2_generalization_local_eager_lazy_001`

```bash
invert-core analyze-run \
  --run core_v2_generalization_local_eager_lazy_001 \
  --config configs/core_v2_generalization_local_eager_lazy.yaml
invert-core summarize-core-v2
```

**Expected per-run outputs:** `eager_lazy_report.md`, `frozen_detector_metadata.json`, `eager_lazy_pole_asymmetry.{md,csv}`

### Class D (BFS/DFS)

**Run ID:** `core_v2_generalization_local_bfs_dfs_001`

```bash
invert-core analyze-run \
  --run core_v2_generalization_local_bfs_dfs_001 \
  --config configs/core_v2_generalization_local_bfs_dfs.yaml
invert-core summarize-core-v2
```

**Expected per-run outputs:** `bfs_dfs_report.md`, `frozen_detector_metadata.json`, `bfs_dfs_negative_control.csv`

### Class E (deterministic/randomized)

**Run ID:** `core_v2_generalization_local_deterministic_randomized_001`

```bash
invert-core analyze-run \
  --run core_v2_generalization_local_deterministic_randomized_001 \
  --config configs/core_v2_generalization_local_deterministic_randomized.yaml
invert-core summarize-core-v2
```

**Expected per-run outputs:** `deterministic_randomized_report.md`, `frozen_detector_metadata.json`, `deterministic_randomized_fixed_seed_control.csv`

---

## 6. Class C pole-asymmetry audit

The audit aggregates existing detection CSVs for the frozen eager/lazy run. Regenerate with:

```bash
python -c "
from invert_core.audit_eager_lazy_pole_asymmetry import run_eager_lazy_pole_asymmetry_audit
from invert_core.tasks import project_root
r = run_eager_lazy_pole_asymmetry_audit('core_v2_generalization_local_eager_lazy_001', project_root())
print('Wrote', r.md_path if r else 'skipped')
"
```

Or use the batch script (analysis replay; may refresh CSVs):

```bash
bash scripts/regenerate_confirmatory_tables.sh
```

**Expected outputs:**

- `results/core_v2/runs/core_v2_generalization_local_eager_lazy_001/eager_lazy_pole_asymmetry.md`
- `results/core_v2/runs/core_v2_generalization_local_eager_lazy_001/eager_lazy_pole_asymmetry.csv`

Or run the dedicated pytest module:

```bash
pytest tests/core_v2/test_audit_eager_lazy_pole_asymmetry.py -v
```

---

## 7. Full regeneration (optional — requires Ollama)

**Warning:** These scripts call local Ollama models and may take substantial time. Archived outputs are included in the v1.0.1 package; full regeneration is optional.

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

Status reflects verification on **2026-06-29** against the archived v1.0.1 package. “Verified” means the command completed successfully and expected output files were present or regenerated consistently.

| Claim | Run ID | Command | Expected output file(s) | Status |
|-------|--------|---------|-------------------------|--------|
| Class B positive control | `core_v2_generalization_local_quadrature_001` | `invert-core analyze-run --run core_v2_generalization_local_quadrature_001 --config configs/core_v2_generalization_local_quadrature.yaml` | `results/core_v2/runs/.../quadrature_report.md`, `frozen_detector_metadata.json` | Verified (archived) |
| Class C support | `core_v2_generalization_local_eager_lazy_001` | `invert-core analyze-run --run core_v2_generalization_local_eager_lazy_001 --config configs/core_v2_generalization_local_eager_lazy.yaml` | `.../eager_lazy_report.md`, `frozen_detector_metadata.json` | Verified (archived) |
| Class D support | `core_v2_generalization_local_bfs_dfs_001` | `invert-core analyze-run --run core_v2_generalization_local_bfs_dfs_001 --config configs/core_v2_generalization_local_bfs_dfs.yaml` | `.../bfs_dfs_report.md`, `frozen_detector_metadata.json` | Verified (archived) |
| Class E support | `core_v2_generalization_local_deterministic_randomized_001` | `invert-core analyze-run --run core_v2_generalization_local_deterministic_randomized_001 --config configs/core_v2_generalization_local_deterministic_randomized.yaml` | `.../deterministic_randomized_report.md`, `frozen_detector_metadata.json` | Verified (archived) |
| Class C pole-asymmetry audit | `core_v2_generalization_local_eager_lazy_001` | pole audit (§6) | `.../eager_lazy_pole_asymmetry.md` | Verified (archived) |
| Cross-run decision report | (all completed runs) | `invert-core summarize-core-v2` | `results/core_v2/core_v2_decision_report.md` | Verified (2026-06-29) |
| Detector/oracle integrity | — | `invert-core smoke-test` | stdout `Smoke test passed.` | Verified (2026-06-29) |
| Unit/integration tests | — | `pytest` | 187 passed | Verified (2026-06-29) |
| Paper figure export | Classes C–E frozen runs | `python scripts/export_paper_figures.py` | `results/core_v2/figures/strip_level_recovery_curves.png` | Verified (2026-06-29) |
| One-command artifact check | — | `bash scripts/verify_artifact.sh` | smoke-test + pytest + tables + checksums + figures | Verified (2026-06-29) |

---

## 10. Frozen detector metadata

Each frozen generalization run directory contains `frozen_detector_metadata.json` with `git_commit`, `detector_files_hash`, and UTC `timestamp`. See `ARTIFACTS.md` for the hash inventory. **Do not edit detector source when verifying archived hashes.**

Documented detector file hashes (SHA256, unchanged in v1.0.1):

| File | Hash |
|------|------|
| `eager_lazy.py` | `1c1abd2bd8816324bf029a7ae06dd36b4e542144dbdab037d083b46ae48aea6b` |
| `bfs_dfs.py` | `10fecb7e623913d63cc69047f041d526d8dfb0e3b5f6db015102228d72d05671` |
| `deterministic_randomized.py` | `ab5e5a91750dbd17c0e87e6bd8338db1fd92ac2fce7c244e3b02c31fbc3e5f23` |
| `quadrature.py` | `c446cbd2ec945cd68cc4e6024d16ad3fb2d0705b424671d73901aba3fe5947a9` |
| `stripping.py` (Class D run) | `5032952fceaf4c6b36e78b3f4414a0df1658d4abb37c53692d88356c82b310e0` |
| `stripping.py` (Class E run) | `aace1f27a9199db78266694f63266c57a782851c4e31fa6126150ad6f338a18b` |

---

## 11. Known limitations

- Confirmatory claims bind to **four frozen Ollama-local generalization runs** on engineered synthetic tasks; commercial APIs and human-written code are out of scope.
- Default verification uses **checksum comparison** (`KEY_OUTPUTS.sha256`); analyze-run replay may diverge if detector sources changed after freeze (see `ZENODO_AUDIT.md` §10).
- Class A (`euler_vs_rk4`) has pilots only; not part of confirmatory aggregates.
- Larger-N robustness runs (`core_v2_robustness_large_n_*`) are **not** part of v1.0.1 confirmatory evidence if present locally; exclude from Zenodo.
- Zenodo DOI: **10.5281/zenodo.21063175** (v1.0.1; see `CITATION.cff`).

---

## 12. Manuscript linkage

LaTeX source of truth is maintained outside this repository (companion TOSEM manuscript). Data Availability references this package (Zenodo DOI: 10.5281/zenodo.21063175).
