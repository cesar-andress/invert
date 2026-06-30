# H09_rep_scaling_hidden_diversity: Repetition scaling at T=0

## Research question

Does increasing N reveal latent diversity without raising temperature?

## INVERT classes

C, D, E

## Status

Preflight scaffold only. No full generation executed.

## Files

- `config.yaml` — experiment skeleton
- `schema.csv` — output column schema
- `go_no_go.json` — decision criteria
- `run_preflight.py` — lightweight readiness checks

## Constraints

- Do not modify frozen Core v2 detectors or frozen runs
- No human annotation; no LLM judges; no external adapters

## Go/no-go

GO if N=30 richness >= 2x N=5 on >=2 deterministic poles
