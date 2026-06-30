#!/usr/bin/env bash
# Print SHA256 digests of primary confirmatory outputs (for diff against archived bundle).
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/repo_root.sh"

KEY_FILES=(
  results/core_v2/core_v2_decision_report.md
  results/core_v2/core_v2_dimension_summary.csv
  results/core_v2/core_v2_model_dimension_summary.csv
  results/core_v2/runs/core_v2_generalization_local_quadrature_001/quadrature_report.md
  results/core_v2/runs/core_v2_generalization_local_quadrature_001/frozen_detector_metadata.json
  results/core_v2/runs/core_v2_generalization_local_eager_lazy_001/eager_lazy_report.md
  results/core_v2/runs/core_v2_generalization_local_eager_lazy_001/eager_lazy_pole_asymmetry.md
  results/core_v2/runs/core_v2_generalization_local_eager_lazy_001/frozen_detector_metadata.json
  results/core_v2/runs/core_v2_generalization_local_bfs_dfs_001/bfs_dfs_report.md
  results/core_v2/runs/core_v2_generalization_local_bfs_dfs_001/frozen_detector_metadata.json
  results/core_v2/runs/core_v2_generalization_local_deterministic_randomized_001/deterministic_randomized_report.md
  results/core_v2/runs/core_v2_generalization_local_deterministic_randomized_001/frozen_detector_metadata.json
)

for f in "${KEY_FILES[@]}"; do
  if [[ ! -f "${f}" ]]; then
    echo "MISSING ${f}" >&2
    exit 1
  fi
  sha256sum "${f}"
done
