# Zenodo Packaging Audit — INVERT Core v2

**Audit date:** 2026-06-29  
**Repository root:** `~/papers/invert/invert/`  
**Manuscript:** `~/papers/invert/paper/` (external; LaTeX source of truth)

This report documents sensitive-data exposure, bloat, and packaging recommendations. **No files were deleted** during this audit.

---

## 1. Executive summary

| Area | Status | Action |
|------|--------|--------|
| API keys / secrets | **Clear** | `.env` gitignored; only `.env.example` with empty placeholders |
| Private user paths | **Minor** | Shell scripts hardcode `~/papers/invert/invert`; document for replicators |
| Large files (>1 MB) | **Clear** | None outside `.venv/` |
| Virtual environments | **Exclude** | `.venv/` (~408 MB) — not for Zenodo |
| Python caches | **Exclude** | `__pycache__/`, `.pytest_cache/` present locally |
| Ollama model weights | **Not in repo** | Models pulled separately by Ollama |
| Core v2 generated data | **Include** | `data/core_v2/` (~56 MB, ~9966 files) — required for reproduction |
| Core v2 results | **Include** | `results/core_v2/` (~4.4 MB) |
| Legacy cloud artifacts | **Review** | Optional subset of `data/raw/openai/`, `data/code/openai/` etc. |
| Frozen metadata | **Verified** | All 4 generalization runs have `frozen_detector_metadata.json` |
| License | **Added** | `LICENSE` (MIT) |
| Citation metadata | **Added** | `CITATION.cff`, `.zenodo.json` |

---

## 2. Secrets and credentials

### Searched patterns

- `.env`, `.env.local` — **not tracked** (`.gitignore` covers these)
- `*.pem`, `*.key` — none found
- `sk-*`, `ghp_*`, populated `OPENAI_API_KEY=` — none in tracked source (only empty placeholders in `.env.example`)

### Environment template

```
.env.example  →  OPENAI_API_KEY=, ANTHROPIC_API_KEY=, GOOGLE_API_KEY=
```

**Recommendation:** Do not upload `.env` if created locally. Zenodo upload should exclude `.env* except .env.example`.

---

## 3. Private / machine-specific paths

| Location | Issue |
|----------|-------|
| `scripts/run_core_v2_*.sh` | `cd ~/papers/invert/invert` — replicators should adjust or run from repo root |
| `README.md`, docs | Reference `~/papers/invert/invert` and `~/papers/invert/paper` |
| `paper/` in `.gitignore` | Manuscript intentionally outside this git repo |

**Recommendation:** Document path substitution in `REPRODUCIBILITY.md` (done). No secrets exposed.

---

## 4. Size and file counts

| Path | Approx. size | Files | Zenodo |
|------|-------------|-------|--------|
| `data/core_v2/` | 56 MB | ~9798 | **Include** |
| `results/core_v2/` | 4.4 MB | — | **Include** |
| `src/` | 1.5 MB | — | **Include** |
| `tests/` | 620 KB | — | **Include** |
| `configs/`, `scripts/`, `prereg/` | <100 KB | — | **Include** |
| `.venv/` | 408 MB | — | **Exclude** |
| `__pycache__/` | scattered | — | **Exclude** |
| `.pytest_cache/` | small | — | **Exclude** |
| Legacy `data/raw/openai/`, etc. | variable | many untracked | **Optional** (not required for Core v2 paper claims) |

No single file >1 MB outside `.venv/`.

---

## 5. Cache and build artifacts (local only)

Found locally (exclude from Zenodo):

- `src/**/__pycache__/`
- `.pytest_cache/`
- `*.pyc`
- `.venv/`
- `*.egg-info/` (if present after install)

LaTeX build artifacts live in `~/papers/invert/paper/` (separate tree): `paper.aux`, `paper.log`, `paper.pdf`, etc.

---

## 6. Ollama / model weights

- Generalization configs reference Ollama tags: `qwen2.5-coder:14b`, `qwen2.5-coder:32b`, `qwen3-coder:30b`, `devstral:latest`
- **No model weights or Ollama blobs** are stored in this repository
- Archived `data/core_v2/raw/` JSON contains prompts and model responses only

---

## 7. Logs

- `*.log` is gitignored
- No persistent application logs in tracked tree
- Per-run reports are Markdown/CSV (intentional artifacts)

---

## 8. Frozen detector metadata verification

| Run ID | File present | Hashes documented |
|--------|--------------|-------------------|
| `core_v2_generalization_local_quadrature_001` | Yes | `integration.py`, `quadrature.py` |
| `core_v2_generalization_local_eager_lazy_001` | Yes | `integration.py`, `quadrature.py`, `eager_lazy.py` (no `stripping.py` in archived file) |
| `core_v2_generalization_local_bfs_dfs_001` | Yes | above + `bfs_dfs.py`, `stripping.py` |
| `core_v2_generalization_local_deterministic_randomized_001` | Yes | above + `deterministic_randomized.py`, `stripping.py` (different hash than Class D) |

Full hash table: see `ARTIFACTS.md`. Hashes were **not modified** during this audit.

---

## 9. Git tracking gaps (pre-upload)

As of audit date, many Core v2 data files under `data/core_v2/` are **untracked** in git but **present on disk**. Zenodo upload should include the full directory tree from disk, not only git-tracked files.

Tracked generalization results in git: partial (summary CSVs + some pilot runs). Full generalization run reports and `data/core_v2/` should be explicitly included in the Zenodo bundle.

---

## 10. Recommended exclusions for Zenodo upload

```
.venv/
venv/
env/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.pyc
*.pyo
.git/
.env
.env.local
*.pem
*.key
.DS_Store
.idea/
.vscode/
*.egg-info/
dist/
build/
htmlcov/
.coverage
```

---

## 11. Recommended inclusions (minimum for paper claims)

```
src/
tests/
configs/
scripts/
prereg/
data/core_v2/
results/core_v2/
pyproject.toml
requirements.txt
README.md
REPRODUCIBILITY.md
ARTIFACTS.md
ZENODO_AUDIT.md
MANIFEST_ZENODO.txt
CITATION.cff
.zenodo.json
LICENSE
.env.example
ARTIFACT.md
```

Optional: legacy prototype under `data/intents/`, `src/invert/`, partial legacy `data/raw/local_stub/`.

---

## 12. Verification commands run (2026-06-29)

| Command | Result |
|---------|--------|
| `pytest` | 187 passed |
| `invert-core smoke-test` | passed |
| `invert-core summarize-core-v2` | wrote 3 summary files |

No full LLM generation was run during this audit.

---

## 13. Open items before Zenodo deposit

1. Assign Zenodo DOI and update `CITATION.cff`, `.zenodo.json`, and manuscript `data_availability.tex`
2. Replace anonymous author placeholders
3. Confirm whether legacy cloud-generated artifacts are included or omitted from upload
4. Ensure `data/core_v2/` and full generalization run directories are bundled
5. Add GitHub repository URL to `CITATION.cff` when public
