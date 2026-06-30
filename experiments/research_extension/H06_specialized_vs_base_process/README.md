# H06_specialized_vs_base_process: Code-specialized vs base process monoculture

## Research question

Do code-specialized models show lower process diversity than base instruct models?

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

GO if coder richness <= 0.5 * base richness on >=2 classes
