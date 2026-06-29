# INVERT — Minimal Falsification Prototype

INVERT studies whether developer intent dimensions are recoverable from generated code.

This prototype runs a controlled experiment: for each programming task and intent dimension, we generate code with contrasting intent values (v0 vs v1), then ask a blind LLM judge to recover those values from the code alone.

**Figure 1** is a heatmap of identifiability by intent dimension and generator model. If the heatmap is flat, the project dies. If it shows non-trivial structure, the project continues.

## Install

```bash
cd ~/papers/invert/invert
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Smoke test (no API keys)

```bash
python scripts/smoke_test.py
```

This runs generate → recover → aggregate → plot using the `local_stub` provider and verifies output files exist.

## First real experiment

1. Copy environment template and set API keys:

```bash
cp .env.example .env
# export OPENAI_API_KEY, ANTHROPIC_API_KEY, and/or GOOGLE_API_KEY
```

2. Generate code with a real model:

```bash
invert generate --models openai --tasks data/intents/tasks.json --repetitions 1
```

3. Run blind recovery:

```bash
invert recover --judge openai --models openai
```

4. Aggregate and plot:

```bash
invert aggregate
invert plot
```

Outputs land in `results/`:

- `recovery.csv` — per-sample recovery rows
- `identifiability_matrix.csv` — accuracy by dimension and model
- `identifiability_heatmap.png` — Figure 1

## Environment variables

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | OpenAI provider |
| `ANTHROPIC_API_KEY` | Anthropic provider |
| `GOOGLE_API_KEY` | Google Gemini provider |

Missing keys only cause errors when that provider is explicitly selected.

## Current limitations

- 10 tasks, 8 intent dimensions, 1 repetition by default
- Correctness computed only for the manipulated dimension
- No deterministic detectors, temperature sweeps, or prompt variants
- `local_stub` is for pipeline testing only, not scientific results
- No database, dashboard, or advanced statistics
