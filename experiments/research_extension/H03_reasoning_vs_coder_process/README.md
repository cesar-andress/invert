# H03_reasoning_vs_coder_process: Reasoning vs coder process strategies

## Research question

Do reasoning models differ in bounded process traces from coder models at matched validity?

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

GO if fingerprint divergence significant on >=2 classes with matched valid_n>=30
