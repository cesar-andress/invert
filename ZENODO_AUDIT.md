# Zenodo Packaging Audit — INVERT Core v2 (v1.0.1)

**Audit date:** 2026-06-30  
**Target release:** GitHub tag `v1.0.1` → Zenodo archival deposit (metadata correction after v1.0.0 extra-metadata failure)  
**Repository:** INVERT replication package (`invert/`)

This report documents sensitive-data exposure, bloat, packaging recommendations, and release readiness. **No scientific CSVs or frozen detector sources were modified** during this audit.

---

## 1. Executive summary (v1.0.1 readiness)

| Area | Status | Notes |
|------|--------|-------|
| Version metadata | **Ready** | `v1.0.1` in `CITATION.cff`, `.zenodo.json`, `pyproject.toml`, `README.md` |
| Zenodo JSON | **Valid** | `python3 -m json.tool .zenodo.json` passes |
| Citation metadata | **Valid** | `CITATION.cff` consistent with `.zenodo.json` |
| API keys / secrets | **Clear** | `.env` gitignored; only `.env.example` with empty placeholders |
| Private user paths | **Documented** | Docs use portable `/path/to/invert`; manuscript external |
| Frozen detector metadata | **Present** | All four confirmatory runs have `frozen_detector_metadata.json` |
| Verification without LLM | **Documented** | `bash scripts/verify_artifact.sh` |
| License | **MIT** | `LICENSE` present |
| Zenodo DOI | **Assigned** | `10.5281/zenodo.21063175` (v1.0.1; in `CITATION.cff`, README, manuscript Data Availability) |
| GitHub URL | **Pending** | Add to `CITATION.cff` when public repository URL is finalized |
| Git working tree | **Not clean** | See §15 — commit or stash before tagging |
| Robustness large-N runs | **Exclude v1.0.1** | Incomplete/experimental; not confirmatory |
| External validation probes | **Include as notes only** | `EXTERNAL_VALIDATION_CLOSURE.md` and sibling feasibility files; exploratory, not confirmatory |
| Third-party clones | **Exclude v1.0.1** | `external_study/` (e.g., EffiBench-X clone); not confirmatory |

**Recommendation:** Tag `v1.0.1` only after committing intended release files and excluding `.venv/`, caches, and incomplete robustness artifacts from the Zenodo upload bundle.

---

## 2. Release description (consistent across README / Zenodo)

- **Version:** v1.0.1  
- **Project:** INVERT  
- **Purpose:** Artifact package for recovering deterministic process signatures from behaviorally equivalent LLM-generated code.  
- **Confirmatory run IDs:**  
  - `core_v2_generalization_local_quadrature_001` (Class B)  
  - `core_v2_generalization_local_eager_lazy_001` (Class C)  
  - `core_v2_generalization_local_bfs_dfs_001` (Class D)  
  - `core_v2_generalization_local_deterministic_randomized_001` (Class E)

---

## 3. Secrets and credentials

### Searched patterns (2026-06-30)

- `.env`, `.env.local` — **not tracked** (`.gitignore`)
- `*.pem`, `*.key`, `id_rsa*` — **none** outside `.venv/`
- `sk-*`, `ghp_*`, populated API keys — **none** in tracked source

### Environment template

```
.env.example  →  OPENAI_API_KEY=, ANTHROPIC_API_KEY=, GOOGLE_API_KEY=
```

**Do not upload** a populated `.env` to Zenodo.

---

## 4. Private / machine-specific paths

| Location | Status |
|----------|--------|
| `scripts/run_core_v2_*.sh` | Portable via `scripts/lib/repo_root.sh` |
| `README.md`, `REPRODUCIBILITY.md` | Use `/path/to/invert` in examples |
| Manuscript LaTeX | External to this repo (by design) |
| `paper/` | Listed in `.gitignore` |

No SSH keys or home-directory secrets found in tracked files.

---

## 5. Size and file counts

| Path | Approx. size | Zenodo v1.0.1 |
|------|-------------|---------------|
| `data/core_v2/` (confirmatory runs) | ~56 MB | **Include** |
| `results/core_v2/` (confirmatory) | ~4.4 MB | **Include** |
| `src/`, `tests/`, `configs/`, `scripts/` | <3 MB | **Include** |
| `.venv/` | ~408 MB | **Exclude** |
| `__pycache__/`, `.pytest_cache/` | small | **Exclude** |
| `data/core_v2/**/core_v2_robustness_large_n_*` | partial local | **Exclude** |
| Legacy cloud `data/raw/openai/` etc. | variable | **Optional** |

No tracked file >1 MB outside `.venv/` or `.git/`.

---

## 6. Cache and build artifacts (local only; exclude from Zenodo)

- `src/**/__pycache__/`
- `.pytest_cache/` (~48 KB locally)
- `.venv/` (~408 MB)
- `*.egg-info/`, `dist/`, `build/`
- LaTeX build artifacts (external manuscript tree)

**Action:** Do not delete automatically; exclude from upload per `MANIFEST_ZENODO.txt`.

---

## 7. Ollama / model weights

- Configs reference Ollama tags: `qwen2.5-coder:14b`, `qwen2.5-coder:32b`, `qwen3-coder:30b`, `devstral:latest`
- **No model weights** stored in repository
- v1.0.1 verification **does not require Ollama**

---

## 8. Frozen detector metadata verification

| Run ID | `frozen_detector_metadata.json` | Documented hashes |
|--------|--------------------------------|-------------------|
| `core_v2_generalization_local_quadrature_001` | Yes | `integration.py`, `quadrature.py` |
| `core_v2_generalization_local_eager_lazy_001` | Yes | `integration.py`, `quadrature.py`, `eager_lazy.py` (no `stripping.py` at freeze) |
| `core_v2_generalization_local_bfs_dfs_001` | Yes | above + `bfs_dfs.py`, `stripping.py` |
| `core_v2_generalization_local_deterministic_randomized_001` | Yes | above + `deterministic_randomized.py`, `stripping.py` |

Full hash table: `ARTIFACTS.md`. Hashes were **not recomputed or modified** in this audit.

---

## 9. Analyze-run replay caveat

Re-running `invert-core analyze-run` **rewrites** per-run CSVs and updates `frozen_detector_metadata.json`. Default v1.0.1 verification (`bash scripts/verify_artifact.sh`) uses **checksum comparison** via `KEY_OUTPUTS.sha256` without analyze-run replay.

Use `INVERT_VERIFY_REPLAY=1` only to test whether current detector code reproduces archived scores.

---

## 10. Recommended Zenodo exclusions

```
.venv/  venv/  env/
__pycache__/  .pytest_cache/  .mypy_cache/  .ruff_cache/
*.pyc  *.pyo  .git/
.env  .env.local  *.pem  *.key
.DS_Store  .idea/  .vscode/
*.egg-info/  dist/  build/  htmlcov/  .coverage
configs/core_v2_robustness_large_n_*.yaml
data/core_v2/**/core_v2_robustness_large_n_*
results/core_v2/runs/core_v2_robustness_large_n_*
results/core_v2/robustness_large_n_*
```

---

## 11. Recommended Zenodo inclusions (minimum for paper claims)

See `MANIFEST_ZENODO.txt`. Minimum:

- Source: `src/`, `tests/`, `configs/`, `scripts/`, `prereg/`
- Data: four frozen generalization run trees under `data/core_v2/`
- Results: `results/core_v2/` confirmatory CSVs/MD + `figures/`
- Metadata: `README.md`, `REPRODUCIBILITY.md`, `ARTIFACTS.md`, `CITATION.cff`, `.zenodo.json`, `LICENSE`, `KEY_OUTPUTS.sha256`, `PAPER_ARTIFACTS.md`

---

## 12. Verification commands (reference)

| Command | Purpose |
|---------|---------|
| `bash scripts/verify_artifact.sh` | Default v1.0.1 check (no LLM) |
| `pytest` | Unit/integration (187 tests, 2026-06-29) |
| `invert-core smoke-test` | Detector/oracle fixtures |
| `invert-core summarize-core-v2` | Re-aggregate archived per-run CSVs |
| `bash scripts/checksum_key_outputs.sh` | Compare to `KEY_OUTPUTS.sha256` |

No full LLM generation required for Zenodo verification.

---

## 13. Version consistency scan (2026-06-30)

| Pattern | Status |
|---------|--------|
| `v0.` / `0.1.0` in release metadata | **Fixed** → `1.0.1` / `v1.0.1` |
| `Process Trinity` as paper title | **Removed** from README title; historical label only in legacy docs if any |
| `closure theorem` / `mathematical completeness` | **Not claimed** in v1.0.1 README |
| Zenodo DOI | **Recorded** | `10.5281/zenodo.21063175` in `CITATION.cff` and docs; not embedded in minimal `.zenodo.json` |
| GitHub URL in `CITATION.cff` | **Omitted** until repository URL is public |

---

## 14. Open items after Zenodo deposit (v1.0.1)

1. ~~**Assign Zenodo DOI**~~ → **Done:** `10.5281/zenodo.21063175` in `CITATION.cff`, README, manuscript `data_availability.tex`
2. **Publish GitHub repository URL** → update `CITATION.cff` `repository-code` when public
3. **Clean git tree** → commit post-deposit metadata updates; do not alter confirmatory CSV contents
4. **Confirm legacy cloud artifacts** included or omitted in future bundle revisions
5. **Upload bundle** per `MANIFEST_ZENODO.txt` (exclude robustness large-N) — satisfied for v1.0.1 deposit
6. ~~**GitHub release** `v1.0.1`~~ → published; Zenodo record linked

---

## 15. Git hygiene (2026-06-30)

```
git log -1 --oneline  →  8ad8415 Updating pilot runs
```

**Modified tracked files (not committed):** metadata docs, some runner scripts, and **confirmatory CSVs** (`core_v2_dimension_summary.csv`, `eager_lazy_pole_asymmetry.csv`, etc.). **Do not alter reported CSV contents for packaging**; either commit the current archived state intentionally or restore from last known-good commit before tagging.

**Untracked (release candidates):** `KEY_OUTPUTS.sha256`, `PAPER_ARTIFACTS.md`, `scripts/verify_artifact.sh`, `scripts/export_paper_figures.py`, `results/core_v2/figures/`, verification helpers.

**Untracked (exclude from v1.0.1):** `core_v2_robustness_large_n_*` configs, data, and partial results.

**Working tree is not clean** — tagging `v1.0.1` today requires a deliberate commit decision.

---

## 16. Sensitive/bloat risks remaining

| Risk | Severity | Mitigation |
|------|----------|------------|
| Local `.venv/` (~408 MB) | High if uploaded | Exclude |
| `.pytest_cache/` | Low | Exclude |
| Incomplete robustness runs | Medium (scope confusion) | Exclude from v1.0.1 |
| Analyze-run replay drift | Medium | Default verify uses checksums only |
| Legacy `data/raw/openai/` untracked blobs | Low–medium | Omit unless explicitly needed |
| TODO DOI/URL placeholders | **Resolved (DOI)** | GitHub URL pending public repo |
| Modified CSVs in working tree | Medium | Resolve before tag |

**No automatic deletions performed.**
