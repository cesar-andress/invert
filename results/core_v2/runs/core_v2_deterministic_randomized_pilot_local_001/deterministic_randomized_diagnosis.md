# Deterministic/Randomized pilot diagnosis (`core_v2_deterministic_randomized_pilot_local_001`)

## Summary

- Generated artifacts inspected: **120**
- Parsed (`ItemProcessor` loads): **120**
- Behavioral pass: **0**
- Behavioral fail: **120**
- Artifacts capturing `visit_fn(...)` return value: **120**

## Verdict

**Prompt/API-contract failure (systematic).** Every artifact defines `ItemProcessor` with the expected class name and constructor, calls `visit_fn` once per item, but treats `visit_fn(item)` as a **map/transform** returning processed values. The benchmark contract requires `visit_fn` to be a void side-effect callback; `process_all()` must return the original input items (set or sorted list), not callback return values.

## Top failure modes

| rank | failure_category | count |
|------|------------------|-------|
| 1 | `output_not_expected_set` | 76 |
| 2 | `exception_during_execution` | 44 |

## Failures by model

- `ollama__devstral__latest`: **30** fails (exception_during_execution=14, output_not_expected_set=16)
- `ollama__qwen2_5-coder__14b`: **30** fails (exception_during_execution=15, output_not_expected_set=15)
- `ollama__qwen2_5-coder__32b`: **30** fails (exception_during_execution=15, output_not_expected_set=15)
- `ollama__qwen3-coder__30b`: **30** fails (output_not_expected_set=30)

## Failures by requested method

- `deterministic`: **60** fails (exception_during_execution=14, output_not_expected_set=46)
- `randomized`: **60** fails (exception_during_execution=30, output_not_expected_set=30)

## Representative failure mechanism

Typical generated pattern (deterministic example):

```python
processed_item = self.visit_fn(item)
processed_items.append(processed_item)
return sorted(processed_items)  # wrong: accumulates callback return values
```

Expected contract:

```python
self.visit_fn(item)  # side effect only; ignore return value
return sorted(self.items)  # or set(self.items)
```

## Notes

- `parsed=true` for all failing artifacts: class loads and constructor accepts `(items, visit_fn, seed=None)`.
- Ordering/randomization logic is often present but unvalidated because behavioral validity fails first on return-value handling.
- Detector ambiguity follows from invalid outputs (`None` sets) or runtime exceptions during repeated trace collection.

See `deterministic_randomized_diagnosis.csv` for per-artifact excerpts.
