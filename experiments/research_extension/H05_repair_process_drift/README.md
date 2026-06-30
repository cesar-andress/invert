# H05_repair_process_drift: Repair-induced process drift

## Research question

Does automated repair preserve process signatures when fixing invalid artifacts?

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

GO if >=15% repaired-valid artifacts flip process pole or fingerprint
