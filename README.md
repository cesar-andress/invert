# INVERT — Replication Package (Core v2)

**Paper:** *INVERT: The Process Trinity of Generated Code* — Recovering Quantity, Order, and Variability Signatures from LLM-Generated Programs (ACM TOSEM manuscript; LaTeX source at `~/papers/invert/paper/`).

This repository packages the **INVERT Core v2** deterministic benchmark: preregistered tasks, behavioral oracles, process-signature detectors, generated code artifacts, frozen generalization runs, and cross-run analysis reports.

## Overview

INVERT tests whether **process intent** (how code computes, not only what it outputs) is recoverable from LLM-generated programs under outcome equivalence.

| Class | Dimension | Role |
|-------|-----------|------|
| A | `euler_vs_rk4` | Positive control (derivative-call identity) |
| B | `trapezoidal_vs_simpson` | Positive control (quadrature weight identity) |
| C | `eager_vs_lazy` | Dynamic quantity / avoidable computation |
| D | `bfs_vs_dfs` | Dynamic traversal order |
| E | `deterministic_vs_randomized` | Inter-execution variability |

Classes **C, D, E** are the novel dynamic process-signature dimensions. The **Process Trinity** (quantity, order, variability) is an empirical design-space label from this repository—not a completeness theorem.

**Reported confirmatory results** come from **frozen generalization runs** using **local Ollama models**. Paid cloud APIs (OpenAI, Anthropic, Google) are optional and not required to verify archived outputs.

## Repository layout

```
invert/
├── README.md                 # this file
├── REPRODUCIBILITY.md        # exact commands and status table
├── ARTIFACTS.md              # inventory of configs, data, results
├── ZENODO_AUDIT.md           # sensitive-data and bloat audit
├── MANIFEST_ZENODO.txt       # intended Zenodo include/exclude lists
├── CITATION.cff / .zenodo.json / LICENSE
├── pyproject.toml            # primary dependency manifest (Python ≥3.10)
├── requirements.txt          # pinned runtime deps (mirror of pyproject)
├── configs/                  # YAML run configurations
├── scripts/                  # shell runners (generalization + pilots)
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

**Requirements:** Python **≥ 3.10** (developed and tested with **3.12**), `git`, and optionally [Ollama](https://ollama.com/) for re-generation (not needed to read archived results).

```bash
cd ~/papers/invert/invert
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Dependencies are declared in `pyproject.toml`; `requirements.txt` lists the same runtime packages for convenience.

## Quick verification (no API keys, no Ollama)

```bash
invert-core smoke-test          # detector + oracle fixture checks
pytest                          # full unit/integration suite
invert-core summarize-core-v2   # regenerate cross-run CSVs and decision report
```

Legacy prototype smoke test (optional):

```bash
python scripts/smoke_test.py    # or: invert smoke-test
```

## Reproducing main paper results

Archived generated code and reports are bundled under `data/core_v2/` and `results/core_v2/`. **Analysis-only reproduction** re-runs detectors on archived code (no LLM calls):

| Claim | Run ID | Analysis command |
|-------|--------|------------------|
| Class B control | `core_v2_generalization_local_quadrature_001` | see `REPRODUCIBILITY.md` |
| Class C | `core_v2_generalization_local_eager_lazy_001` | see `REPRODUCIBILITY.md` |
| Class D | `core_v2_generalization_local_bfs_dfs_001` | see `REPRODUCIBILITY.md` |
| Class E | `core_v2_generalization_local_deterministic_randomized_001` | see `REPRODUCIBILITY.md` |

**Full re-generation** (optional) requires Ollama with the models listed in each config YAML and the shell scripts under `scripts/run_core_v2_generalization_local_*.sh`. See `REPRODUCIBILITY.md` for exact commands.

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
- `ARTIFACTS.md` — file inventory
- `ZENODO_AUDIT.md` — packaging audit (secrets, bloat, exclusions)
- `MANIFEST_ZENODO.txt` — intended Zenodo file list
- `ARTIFACT.md` — legacy prototype artifact notes (superseded for Core v2 by this README)

## Citation

See `CITATION.cff`. Zenodo DOI: **TODO** (to be assigned on upload).

## License

MIT — see `LICENSE`.
