# H08_cross_class_process_coupling: Cross-class process coupling

## Research question

Are model process fingerprints correlated across C/D/E?

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

GO if |Spearman rho|>=0.5 between >=2 class pairs for >=3 models
