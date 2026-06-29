# INVERT Research Artifact

This repository is the minimal INVERT falsification prototype: a controlled experiment to test whether developer intent dimensions are recoverable from generated code.

## Purpose

For each programming task and intent dimension, the pipeline generates code under contrasting intent values (v0 vs v1), then runs a blind LLM judge to recover those values from code alone. The primary output is an identifiability heatmap (Figure 1): dimension × generator model recovery accuracy.

## Smoke test (no API keys)

```bash
cd ~/papers/invert/invert
python -m venv .venv
source .venv/bin/activate
pip install -e .
python scripts/smoke_test.py
```

Expected outputs:

- `results/recovery.csv`
- `results/identifiability_matrix.csv`
- `results/identifiability_heatmap.png`

## Pilot run (API keys required)

```bash
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...

bash scripts/run_pilot_001.sh
```

Or step by step:

```bash
invert check-apis --models openai,anthropic
invert generate --config configs/pilot.yaml --dry-run
invert generate --config configs/pilot.yaml
invert recover --config configs/pilot.yaml
invert aggregate --run pilot_001
invert plot --run pilot_001
```

Pilot outputs:

- `results/runs/pilot_001/metadata.json`
- `results/runs/pilot_001/recovery.csv`
- `results/runs/pilot_001/identifiability_matrix.csv`
- `results/runs/pilot_001/identifiability_heatmap.png`

Raw generated artifacts are stored under `data/raw/`, extracted code under `data/code/`, and recovery judgments under `data/recovery/`.

## Reproducibility notes

- Task definitions: `data/intents/tasks.json`
- Model settings: `configs/models.yaml`
- Pilot configuration: `configs/pilot.yaml`
- Run metadata records tasks, models, repetitions, temperature, and git commit when available
- Use `invert generate --config configs/pilot.yaml --dry-run` to inspect the generation plan without API calls
- Existing outputs are skipped when `overwrite: false`; pass `--overwrite` to regenerate
- API keys are read from environment variables only (`.env` is not tracked)
- `local_stub` enables end-to-end pipeline testing without external APIs
