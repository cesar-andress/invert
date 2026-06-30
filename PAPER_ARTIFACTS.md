# Paper Artifacts — Tables and Figures

Maps ACM TOSEM manuscript outputs (`~/papers/invert/paper/`) to files in this replication package.

**Policy:** Confirmatory claims use four frozen generalization runs only. Regeneration commands do **not** call LLMs when archived `data/core_v2/code/` is present.

---

## One-command verification

```bash
bash scripts/verify_artifact.sh
```

Runs: `smoke-test` → `pytest` → `summarize-core-v2` + pole audit → checksum diff against `KEY_OUTPUTS.sha256` → `export_paper_figures.py`.

Set `INVERT_VERIFY_REPLAY=1` to also re-run `analyze-run` on all four frozen runs (rewrites detection CSVs; use for detector replay studies only).

---

## Tables in the manuscript

All numeric tables in the paper trace to CSV/Markdown exports below. LaTeX copies values manually; replicators should treat these files as source of truth.

| Manuscript label | Source file(s) | Regenerate |
|------------------|----------------|------------|
| `tab:frozen-runs` | Run IDs in configs + `results/core_v2/runs/` | N/A (fixed IDs) |
| `tab:dimension-snapshot` | `results/core_v2/core_v2_dimension_summary.csv` | `invert-core summarize-core-v2` |
| `tab:class-c-recovery`, `tab:pole-asymmetry-main` | `.../eager_lazy_report.md`, `.../eager_lazy_pole_asymmetry.{md,csv}` | `analyze-run` + pole audit (§REPRODUCIBILITY) |
| `tab:class-d-recovery` | `.../bfs_dfs_report.md`, `bfs_dfs_valid_only_summary.csv` | `analyze-run` |
| `tab:class-e-recovery` | `.../deterministic_randomized_report.md` | `analyze-run` |
| `tab:trinity-summary` | Derived from per-run valid-only summaries + `core_v2_dimension_summary.csv` | `regenerate_confirmatory_tables.sh` |
| `tab:failures` | Documented in run reports + `core_v2_decision_report.md` | manual audit of run dirs |
| `tab:app:frozen-evidence` | `core_v2_decision_report.md` §Frozen generalization evidence | `summarize-core-v2` |
| `tab:app:artifact-index` | This repository tree | static index |
| `tab:behavioral-oracles`, `tab:detectors`, `tab:stripping`, `tab:survival-rule`, `tab:controls`, `tab:family1-overview` | Protocol definitions in `prereg/`, `configs/`, `src/invert_core/` | code inspection |

**Batch regeneration:**

```bash
bash scripts/regenerate_confirmatory_tables.sh
invert-core summarize-core-v2   # included in script above
```

---

## Figures in the manuscript

| Manuscript figure | Status | Regenerate |
|-------------------|--------|------------|
| `fig:pipeline`, `fig:process-trinity` | LaTeX placeholders in `paper/introduction.tex` | Not automated; diagram export TODO in LaTeX tree |
| `fig:strip-curves` | Placeholder in LaTeX; supplementary export available | `python scripts/export_paper_figures.py` → `results/core_v2/figures/strip_level_recovery_curves.png` |
| `fig:app:strip-heatmap`, `fig:app:negative-controls`, `fig:app:failures` | LaTeX placeholders | Partial: strip curves only; heatmap/panel exports TODO |

The legacy `invert plot` command (`src/invert/plot.py`) targets **prototype** results under `results/runs/`, not Core v2 paper claims.

---

## Checksums

After regeneration, compare against the archived baseline:

```bash
bash scripts/checksum_key_outputs.sh
diff KEY_OUTPUTS.sha256 <(bash scripts/checksum_key_outputs.sh)
```

---

## Manuscript (external)

LaTeX source: `~/papers/invert/paper/` (separate tree; compile with `./build.sh`). Zenodo deposit may bundle paper PDF separately or link via `related_identifiers` in `.zenodo.json`.
