# H01_temperature_process_diversity: Temperature and process trace diversity

## Research question

Does sampling temperature increase bounded process-trace diversity among valid artifacts?

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

GO if >=2 dynamic classes show Shannon H increase >=0.5 bits from T=0 to T=0.8 for >=2 models with valid_rate>=0.5
