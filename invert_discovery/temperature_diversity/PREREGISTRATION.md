# H01 Temperature Pilot — Preregistration

**RQ-H01:** Does decoding temperature increase process-level diversity while preserving behavioral correctness and requested process poles?

**Literature:** Lee et al. 2025 (EMNLP); Hong et al. 2024.

**Scope:** Pilot only — not full H01 study.

| Parameter | Value |
|-----------|-------|
| Models | `ollama:qwen2.5-coder:14b`, `ollama:qwen3-coder:30b` |
| Temperatures | 0.0, 0.4, 0.8 |
| Repetitions | 10 per (model, T, task, pole) |
| Strip | `raw` only |
| Class C tasks | `mixed_signed_vector`, `small_positive_vector` |
| Class D tasks | `branching_1`, `linear_chain` |
| Class E tasks | `letters_8`, `numbers_10` |
| Data root | `data/discovery/h01_temperature_pilot/` |
| Results | `results/research_extension/H01_temperature/` |

**Not modified:** Core v2 detectors, frozen runs, paper.

**Go if:** (1) C or D CI entropy increase with stable recovery, OR (2) monotonic entropy vs T on C/D, OR (3) model curves diverge.

**No-go / abandon if:** only E:randomized diversifies (same as internal preflight).
