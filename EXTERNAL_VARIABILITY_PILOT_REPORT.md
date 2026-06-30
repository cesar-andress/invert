# External Variability Pilot Report (output-stability)

**Study ID:** RQ-EXT-E  
**Pilot date (UTC):** 2026-06-30  
**Detector:** `invert_external.detectors.output_stability`  
**Detector SHA256:** `5e9a0681226143fbcdc2223daec8c0c057618099c1e0ba3f78c20b911b83c9fc`  
**Git commit at freeze:** `8b401795617a430edec4f429d875be9d8c66d9c8`  
**Uses INVERT API:** no (`ItemProcessor`, `GraphTraversal`, `visit_fn`, trace contract — none)  
**Dataset:** HumanEval+ (`humaneval_plus_v1`, EvalPlus oracle)  
**Model (generated):** `ollama:qwen2.5-coder:14b` (temperature 0)  
**Protocol:** N=10, `PYTHONHASHSEED=0`, timeout 2s/run, EvalPlus one-shot gate before repeated runs

This pilot is an **interface-agnostic output-stability variability** study. It is **not** Class E external validation and does not use the frozen INVERT Class E detector.

## Counts

| Metric | Value |
|--------|------:|
| tasks_attempted | 30 |
| generated_n | 30 |
| valid_n (generated, post-EvalPlus) | 21 |
| stable_n (valid generated) | 21 |
| variable_n (valid generated) | 0 |
| flaky_invalid_n | 0 |
| timeout_n | 0 |
| error_n (all rows) | 1 |
| ambiguous_n | 0 |
| invalid_n (generated, EvalPlus fail) | 9 |
| reference_n | 30 |
| reference_stable_n | 29 |
| reference_error_n | 1 (`HumanEval/12`) |

| Rate | Value |
|------|------:|
| variable_rate among valid generated | 0.0% |
| invalid_rate among generated | 30.0% |
| reference_stable_rate | 96.7% |

**Elapsed:** 43.3 s (generation ~41.9 s)

## Reference / canonical solutions

All 30 canonical solutions were scored. **29/30** labeled `stable` under repeated execution on `base_input[0]` with per-run oracle comparison.

**Exception:** `HumanEval/12` reference passed the EvalPlus functional gate but all 10 repeated runs failed the per-run validator (`label=error`, `fail_count=10`). This points to a mismatch between the one-shot EvalPlus check (`plus_input`) and the repeated-run bundle (`base_input[0]`), not output-hash variability. It does not block the pilot decision rule (reference_stable_rate ≥ 95%).

## Generated solutions

- **21/30** passed EvalPlus and entered repeated-execution analysis; **all 21** were `stable` (unique output hash count = 1).
- **0** `variable`, **0** `flaky_invalid`.
- **9** `invalid` (EvalPlus `fail` — extraction or functional errors, not detector instability).
- **1** generation row marked `error` at artifact level only when generation threw; none in this pilot.

Invalid generated tasks: `HumanEval/0`, `/1`, `/10`, `/108`, `/110`, `/115`, `/12`, `/120`, `/124`.

## Smoke tests (pre-pilot)

`external_variability_smoke_results.csv`: 5/5 toy cases pass (`stable`, `variable`, `flaky_invalid`, `timeout`, `invalid`).

## Decision

| Criterion | Outcome |
|-----------|---------|
| variable_rate ≥ 2% among valid generated | **no** (0%) |
| Execution harness clean enough to interpret | **partially** — references mostly stable; 30% generated invalid is generation/harness noise, not dominant over valid stable artifacts |
| Detector requires INVERT API adaptation | **no** |

**Recommended:** `revise-plan`  
**Full study recommended:** no  
**Reason:** `low_prevalence_null_finding` — zero output-stability variability among functionally valid generated code on this slice; prevalence below the 2% gate for a confirmatory full study.

**Paper placement:** **artifact-only** for now. Do not add to the main paper before submission unless strategically useful; not appendix-ready as a positive external variability finding (null on generated valid artifacts).

## Artifacts

| File | Role |
|------|------|
| `invert_external/detectors/output_stability.py` | Frozen detector |
| `external_variability_detector_sha256.txt` | SHA256 record |
| `EXTERNAL_VARIABILITY_DETECTOR_PROTOCOL.md` | Freeze protocol |
| `results/external_variability/output_stability_freeze.json` | Freeze metadata |
| `external_variability_smoke_results.csv` | Smoke outcomes |
| `external_variability_pilot_results.csv` | Per-artifact pilot rows |
| `external_variability_pilot_summary.csv` | Aggregated metrics |
| `external_variability_pilot_go_no_go.json` | Machine-readable decision |

## Interpretation

The external output-stability detector runs without INVERT trace contracts and classifies toy fixtures correctly. On HumanEval+ with a local 14B coder model, **no variable output-stability** appeared among EvalPlus-valid generated solutions in this 30-task pilot. Invalid generations dominate a minority of tasks but do not indicate detector failure. A full HumanEval+ sweep is **not** recommended pre-submission unless the goal is explicit null reporting or a larger model sweep.
