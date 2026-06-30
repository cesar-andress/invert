# H02_neutral_prompt_process_bias: Neutral-prompt process pole bias

## Research question

Do models default to stable process poles when pole names are omitted from prompts?

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

GO if >=2 models show >=70% default to one detected pole on >=2 classes with valid_rate>=0.4
