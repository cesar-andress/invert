# Process Trace Diversity Preflight

Internal frozen-run discovery analysis on bounded traces already emitted in Core v2 detection CSVs.
Not external validation. Not interface-agnostic recovery. Not a claim of real-world ecological validity.

## Trace data availability

- **trace data available:** True

- **Class B** (`core_v2_generalization_local_quadrature_001`): csv_exists=True, trace_fields_present=True, recovered_rows=450, fields=['coefficient_literals', 'function_eval_pattern', 'has_endpoint_half_weights', 'has_simpson_4_2_pattern']
- **Class C** (`core_v2_generalization_local_eager_lazy_001`): csv_exists=True, trace_fields_present=True, recovered_rows=555, fields=['trace']
- **Class D** (`core_v2_generalization_local_bfs_dfs_001`): csv_exists=True, trace_fields_present=True, recovered_rows=600, fields=['visit_trace']
- **Class E** (`core_v2_generalization_local_deterministic_randomized_001`): csv_exists=True, trace_fields_present=True, recovered_rows=600, fields=['traces']

## Coverage

- classes analyzed: B, C, D, E
- ecology cells: 441
- cells with non-zero diversity: 20
- stripping pairs (raw vs format_normalized): 87
- stripping pairs with diversity at both levels: 3

## Go / no-go

- **recommended:** `maybe`
- **reason:** single_dynamic_class_nonzero_diversity_randomized_pole_only
- dynamic classes with diversity: ['E']
- diverse cells by class:pole: {'E:randomized': 20}
- diversity outside Class E randomized pole: False

## Strongest diversity examples

- Class E | letters_8 | randomized | ollama__qwen3-coder__30b | format_normalized: unique=5/5, H=1.6094
- Class E | letters_8 | randomized | ollama__qwen3-coder__30b | no_comments: unique=5/5, H=1.6094
- Class E | letters_8 | randomized | ollama__qwen3-coder__30b | no_imports: unique=5/5, H=1.6094
- Class E | letters_8 | randomized | ollama__qwen3-coder__30b | raw: unique=5/5, H=1.6094
- Class E | letters_8 | randomized | ollama__qwen3-coder__30b | renamed: unique=5/5, H=1.6094
- Class E | mixed_tokens | randomized | ollama__qwen3-coder__30b | format_normalized: unique=5/5, H=1.6094
- Class E | mixed_tokens | randomized | ollama__qwen3-coder__30b | no_comments: unique=5/5, H=1.6094
- Class E | mixed_tokens | randomized | ollama__qwen3-coder__30b | no_imports: unique=5/5, H=1.6094
- Class E | mixed_tokens | randomized | ollama__qwen3-coder__30b | raw: unique=5/5, H=1.6094
- Class E | mixed_tokens | randomized | ollama__qwen3-coder__30b | renamed: unique=5/5, H=1.6094

## Model × class summary

- Class B | ollama__devstral__latest: 0/30 diverse cells, max_unique=1
- Class B | ollama__qwen2_5-coder__14b: 0/30 diverse cells, max_unique=1
- Class B | ollama__qwen3-coder__30b: 0/30 diverse cells, max_unique=1
- Class C | ollama__devstral__latest: 0/30 diverse cells, max_unique=1
- Class C | ollama__qwen2_5-coder__14b: 0/30 diverse cells, max_unique=1
- Class C | ollama__qwen2_5-coder__32b: 0/30 diverse cells, max_unique=1
- Class C | ollama__qwen3-coder__30b: 0/21 diverse cells, max_unique=1
- Class D | ollama__devstral__latest: 0/30 diverse cells, max_unique=1
- Class D | ollama__qwen2_5-coder__14b: 0/30 diverse cells, max_unique=1
- Class D | ollama__qwen2_5-coder__32b: 0/30 diverse cells, max_unique=1
- Class D | ollama__qwen3-coder__30b: 0/30 diverse cells, max_unique=1
- Class E | ollama__devstral__latest: 3/30 diverse cells, max_unique=2
- Class E | ollama__qwen2_5-coder__14b: 1/30 diverse cells, max_unique=2
- Class E | ollama__qwen2_5-coder__32b: 1/30 diverse cells, max_unique=2
- Class E | ollama__qwen3-coder__30b: 15/30 diverse cells, max_unique=5

## Caveat

All 20 diverse cells are Class E with requested pole `randomized`. Classes C and D show monoculture among valid, correctly recovered artifacts. Class B (structural fingerprint baseline) is also monoculture. Interpret diversity as cross-rep implementation variation on the randomized pole, not as unexpected process biodiversity on deterministic/eager/BFS poles.

## Interpretation

- **paper section potential:** maybe — appendix or short Discussion pointer unless diversity strengthens
- **full PEA worth implementing:** not recommended — diversity confined to Class E randomized pole (semantics-aligned, not hidden biodiversity)

