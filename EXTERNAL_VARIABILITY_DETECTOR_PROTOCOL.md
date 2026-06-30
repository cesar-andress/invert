# External Output-Stability Detector — Frozen Protocol

**Study ID:** RQ-EXT-E  
**Detector module:** `invert_external.detectors.output_stability`  
**Source file:** `invert_external/detectors/output_stability.py`  
**SHA256 file:** `external_variability_detector_sha256.txt`

This detector is **separate** from the frozen INVERT Class E detector (`deterministic_randomized.py`). It is **not** Class E external validation.

## Requirements

- No `ItemProcessor`, `GraphTraversal`, `visit_fn`, or INVERT harness APIs
- No wrapper that imposes an INVERT trace contract
- Classification by repeated-execution **output hash stability** only

## Labels (frozen)

| Label | Rule |
|-------|------|
| `stable` | All N runs pass per-run validation and `unique_output_hash_count == 1` |
| `variable` | All N runs pass and `unique_output_hash_count > 1` |
| `invalid` | Official EvalPlus functional validation fails (one-shot) |
| `flaky_invalid` | Some repeated runs pass validation and some fail |
| `timeout` | Any run exceeds `timeout_sec` |
| `error` | Execution error on repeated runs (all fail) |
| `ambiguous` | Output cannot be normalized safely |

## Parameters (frozen before pilot)

| Parameter | Value |
|-----------|-------|
| `run_count` | 10 |
| `timeout_sec` | 2.0 |
| `PYTHONHASHSEED` | `0` (set in runner environment) |
| Functional gate | EvalPlus augmented tests (one-shot) |
| Generation temperature | 0 |

## Freeze discipline

1. Run `python scripts/smoke_output_stability.py`
2. Record SHA256 in `external_variability_detector_sha256.txt`
3. Do **not** modify `output_stability.py` after freeze before scoring

## Commands

```bash
python scripts/smoke_output_stability.py
pytest tests/invert_external/test_output_stability.py -q
python scripts/run_output_stability_pilot.py
```

## Smoke fixtures

`tests/invert_external/fixtures/toy_*.py` (not confirmatory evidence)
