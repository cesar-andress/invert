# INVERT Core v2 — F1.4 BFS/DFS Report (`core_v2_bfs_dfs_pilot_local_001`)

## 1. Generation validity (branching tasks)

- Generated artifacts: **120**
- Parsed at raw level: **120**
- Valid behavioral artifacts: **120**
- Invalid artifacts: **0**

## 2. Primary branching-graph recovery

| strip_level | valid_detector_accuracy | valid_ambiguous_rate |
|-------------|-------------------------|----------------------|
| raw | 1.0000 | 0.0000 |
| format_normalized | 1.0000 | — |

## 3. Linear-chain negative control

Reference stub implementations on `linear_chain` (`bfs_dfs_negative_control.csv`). BFS and DFS visit nodes in identical order; recovery should collapse to ambiguous.

- Negative-control ambiguous rate (reference stubs, all strip levels): **1.0000**

## 4. Per-pole manipulation success (branching, valid artifacts, raw)

| requested method | manipulation_success_rate | rule |
|------------------|---------------------------|------|
| bfs | 1.0000 | visit trace matches BFS order only |
| dfs | 1.0000 | visit trace matches DFS order only |

## 5. Recovery conditioned on genuine poles (branching, raw)

| requested method | genuine_n | detector_accuracy |
|------------------|-----------|-------------------|
| bfs (genuine BFS only) | 60 | 1.0000 |
| dfs (genuine DFS only) | 60 | 1.0000 |

## 6. Model ranking (valid-only primary recovery)

| rank | model | generated_n | valid_n | valid_artifact_rate | valid_accuracy_raw | valid_accuracy_format_normalized | valid_ambiguous_rate_raw | f1_4_survives |
|------|-------|-------------|---------|---------------------|---------------------|--------------------------------|--------------------------|---------------|
| 1 | Devstral:latest | 30 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |
| 2 | Qwen2.5-coder:14b | 30 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |
| 3 | Qwen2.5-coder:32b | 30 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |
| 4 | Qwen3-coder:30b | 30 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | pass |

## 7. Local model conclusions

### Models supporting F1.4

- Devstral:latest, Qwen2.5-coder:14b, Qwen2.5-coder:32b, Qwen3-coder:30b

## 8. F1.4 decision (per model)

Preregistered rule: valid_n >= 20, valid_detector_accuracy >= 0.9 at raw and format_normalized, valid_ambiguous_rate <= 0.1.

### Order signature vs mathematical identity

BFS and DFS visit the same reachable set with the same number of visit_fn calls; only traversal order differs.

## 9. All-generated summary

| model | task | method | strip_level | all_generated_n | accuracy | behavioral_pass | ambiguous |
|-------|------|--------|-------------|-----------------|----------|-----------------|-----------|
| ollama__devstral__latest | branching_1 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_1 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_1 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_1 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_1 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_1 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_1 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_1 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_1 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_1 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_2 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_2 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_2 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_2 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_2 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_2 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_2 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_2 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_2 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_2 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_3 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_3 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_3 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_3 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_3 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_3 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_3 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_3 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_3 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__devstral__latest | branching_3 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_1 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_1 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_1 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_1 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_1 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_1 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_1 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_1 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_1 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_1 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_2 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_2 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_2 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_2 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_2 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_2 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_2 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_2 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_2 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_2 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_3 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_3 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_3 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_3 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_3 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_3 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_3 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_3 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_3 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__14b | branching_3 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_1 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_1 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_1 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_1 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_1 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_1 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_1 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_1 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_1 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_1 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_2 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_2 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_2 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_2 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_2 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_2 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_2 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_2 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_2 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_2 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_3 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_3 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_3 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_3 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_3 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_3 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_3 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_3 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_3 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen2_5-coder__32b | branching_3 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_1 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_1 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_1 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_1 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_1 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_1 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_1 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_1 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_1 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_1 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_2 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_2 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_2 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_2 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_2 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_2 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_2 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_2 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_2 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_2 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_3 | bfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_3 | bfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_3 | bfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_3 | bfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_3 | bfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_3 | dfs | format_normalized | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_3 | dfs | no_comments | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_3 | dfs | no_imports | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_3 | dfs | raw | 5 | 1.0000 | 1.0000 | 0.0000 |
| ollama__qwen3-coder__30b | branching_3 | dfs | renamed | 5 | 1.0000 | 1.0000 | 0.0000 |
