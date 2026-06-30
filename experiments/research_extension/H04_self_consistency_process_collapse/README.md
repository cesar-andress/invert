# H04_self_consistency_process_collapse: Self-consistency process diversity collapse

## Research question

Does pass@k-style selection reduce process diversity among valid samples?

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

GO if median diversity_loss>=0.3 bits on >=2 classes
