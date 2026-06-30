#!/usr/bin/env bash
# Re-run detectors on archived code and regenerate cross-run tables (no LLM calls).
# Warning: analyze-run rewrites per-run CSVs. Use only when validating detector replay;
# archived Zenodo bundle values match the committed CSVs at deposit time.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/repo_root.sh"

echo "==> analyze-run (frozen generalization, analysis replay)"
invert-core analyze-run \
  --run core_v2_generalization_local_quadrature_001 \
  --config configs/core_v2_generalization_local_quadrature.yaml
invert-core analyze-run \
  --run core_v2_generalization_local_eager_lazy_001 \
  --config configs/core_v2_generalization_local_eager_lazy.yaml
invert-core analyze-run \
  --run core_v2_generalization_local_bfs_dfs_001 \
  --config configs/core_v2_generalization_local_bfs_dfs.yaml
invert-core analyze-run \
  --run core_v2_generalization_local_deterministic_randomized_001 \
  --config configs/core_v2_generalization_local_deterministic_randomized.yaml

echo "==> Class C pole-asymmetry audit"
python -c "
from invert_core.audit_eager_lazy_pole_asymmetry import run_eager_lazy_pole_asymmetry_audit
from invert_core.tasks import project_root
r = run_eager_lazy_pole_asymmetry_audit('core_v2_generalization_local_eager_lazy_001', project_root())
print('Wrote', r.md_path)
"

echo "==> summarize-core-v2"
invert-core summarize-core-v2

echo "Confirmatory tables regenerated under results/core_v2/"
