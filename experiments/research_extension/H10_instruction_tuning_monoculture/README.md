# H10_instruction_tuning_monoculture: Instruction tuning process monoculture

## Research question

Do instruct/chat checkpoints show lower process diversity than base models?

## INVERT classes

derived

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

GO if instruct richness < base on >=3 classes
