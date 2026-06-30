# INVERT — Replication Package (Core v2)

**Version:** v1.0.1  
**Project:** INVERT — artifact package for recovering deterministic process signatures from behaviorally equivalent LLM-generated code.

**Paper:** *INVERT: Recovering Quantity, Order, and Variability Signatures from Behaviorally Equivalent Generated Code* (ACM TOSEM manuscript; LaTeX source maintained separately from this repository).

This repository packages **INVERT Core v2**: preregistered tasks, behavioral oracles, frozen rule-based detectors, generated code artifacts, frozen generalization runs, and cross-run analysis reports.

## Overview

INVERT tests whether **process signatures** (how code computes under instrumentation, not only what it outputs) are recoverable from LLM-generated programs under outcome equivalence.

| Class | Dimension | Role |
|-------|-----------|------|
| A | `euler_vs_rk4` | Positive control (derivative-call identity) |
| B | `trapezoidal_vs_simpson` | Positive control (quadrature weight identity) |
| C | `eager_vs_lazy` | Dynamic quantity / avoidable computation |
| D | `bfs_vs_dfs` | Dynamic traversal order |
| E | `deterministic_vs_randomized` | Inter-execution variability |

Classes **C, D, E** are the dynamic process-signature evidence. Quantity, order, and variability are empirical labels for those three families in the explored benchmark space—not a claim of mathematical completeness.

**Reported confirmatory results** come from **frozen generalization runs** using **local Ollama models**. Paid cloud APIs are optional and not required to verify archived outputs.

## Frozen generalization run IDs (confirmatory)

| Class | Run ID |
|-------|--------|
| B | `core_v2_generalization_local_quadrature_001` |
| C | `core_v2_generalization_local_eager_lazy_001` |
| D | `core_v2_generalization_local_bfs_dfs_001` |
| E | `core_v2_generalization_local_deterministic_randomized_001` |

## Repository layout

```
invert/
├── README.md                 # this file
├── REPRODUCIBILITY.md        # exact commands and status table
├── ARTIFACTS.md              # inventory of configs, data, results
├── ZENODO_AUDIT.md           # sensitive-data and bloat audit
├── MANIFEST_ZENODO.txt       # intended Zenodo include/exclude lists
├── PAPER_ARTIFACTS.md        # manuscript table/figure → file mapping
├── KEY_OUTPUTS.sha256        # baseline digests for confirmatory outputs
├── CITATION.cff / .zenodo.json / LICENSE
├── pyproject.toml            # primary dependency manifest (Python ≥3.10)
├── requirements.txt          # pinned runtime deps (mirror of pyproject)
├── configs/                  # YAML run configurations
├── scripts/                  # shell runners (generalization + verification)
├── prereg/                   # preregistered task registry and predictions
├── data/
│   ├── core_v2/              # Core v2 raw responses, generated code, stripped variants
│   └── intents/              # legacy prototype tasks
├── src/
│   ├── invert/               # legacy falsification CLI (`invert`)
│   └── invert_core/          # Core v2 CLI (`invert-core`), detectors, oracles
├── tests/core_v2/            # pytest suite + fixtures
└── results/core_v2/          # per-run reports + cross-run summaries
```

## Installation

**Requirements:** Python **≥ 3.10** (developed and tested with **3.12**), `git`, and optionally [Ollama](https://ollama.com/) for optional re-generation (not needed to read archived results).

```bash
cd /path/to/invert   # repository root (extracted Zenodo bundle or git clone)
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Dependencies are declared in `pyproject.toml`; `requirements.txt` lists the same runtime packages for convenience.

## Quick verification (no API keys, no Ollama, no LLM regeneration)

```bash
bash scripts/verify_artifact.sh   # smoke-test + pytest + summarize + checksums + figures
```

Or step by step:

```bash
invert-core smoke-test          # detector + oracle fixture checks
pytest                          # full unit/integration suite
invert-core summarize-core-v2   # regenerate cross-run tables from archived per-run CSVs
bash scripts/checksum_key_outputs.sh
python scripts/export_paper_figures.py
```

Optional detector replay (**may rewrite per-run CSVs**; not used for default v1.0.1 verification):

```bash
INVERT_VERIFY_REPLAY=1 bash scripts/verify_artifact.sh
```

Legacy prototype smoke test (optional):

```bash
python scripts/smoke_test.py    # or: invert smoke-test
```

## Reproducing main paper results

Archived generated code and reports are bundled under `data/core_v2/` and `results/core_v2/`. **Analysis-only reproduction** re-runs detectors on archived code (no LLM calls). See `REPRODUCIBILITY.md` for exact commands per run ID.

**Full re-generation** (optional) requires Ollama with the models listed in each config YAML and the shell scripts under `scripts/run_core_v2_generalization_local_*.sh`.

## Reading final reports

| Output | Path |
|--------|------|
| Cross-run decision report | `results/core_v2/core_v2_decision_report.md` |
| Dimension summary CSV | `results/core_v2/core_v2_dimension_summary.csv` |
| Model × dimension CSV | `results/core_v2/core_v2_model_dimension_summary.csv` |
| Per-run reports | `results/core_v2/runs/<run_id>/*_report.md` |
| Frozen detector metadata | `results/core_v2/runs/<run_id>/frozen_detector_metadata.json` |
| Class C pole-asymmetry audit | `results/core_v2/runs/core_v2_generalization_local_eager_lazy_001/eager_lazy_pole_asymmetry.md` |

## Environment variables (optional)

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI provider (legacy / optional) |
| `ANTHROPIC_API_KEY` | Anthropic provider (optional) |
| `GOOGLE_API_KEY` | Google Gemini provider (optional) |

Copy `.env.example` to `.env` for local development. **No API keys are required** to verify Core v2 archived results or run `pytest` / `invert-core smoke-test`.

## CLI entry points

```bash
invert-core --help    # Core v2: generate, analyze-run, summarize-core-v2, smoke-test, …
invert --help         # Legacy prototype
```

## Further documentation

- `REPRODUCIBILITY.md` — command matrix and reproduction status
- `ARTIFACTS.md` — file inventory and frozen detector hashes
- `PAPER_ARTIFACTS.md` — manuscript table/figure mapping
- `ZENODO_AUDIT.md` — packaging audit (secrets, bloat, exclusions)
- `MANIFEST_ZENODO.txt` — intended Zenodo file list
- `ARTIFACT.md` — legacy prototype artifact notes

## Citation

**Artifact:** INVERT Core v2 Replication Package, v1.0.1.  
**DOI:** [10.5281/zenodo.21063175](https://doi.org/10.5281/zenodo.21063175)  
**URL:** https://doi.org/10.5281/zenodo.21063175

See also `CITATION.cff` for machine-readable metadata.

## License

MIT — see `LICENSE`.
