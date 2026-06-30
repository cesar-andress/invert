#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/repo_root.sh"


MODELS="ollama:qwen3-coder:30b,ollama:devstral:latest,ollama:qwen2.5-coder:14b"
CONFIG="configs/core_v2_generalization_local_quadrature.yaml"
RUN="core_v2_generalization_local_quadrature_001"

invert-core check-apis --models "${MODELS}"
invert-core generate --config "${CONFIG}" --dry-run
invert-core generate --config "${CONFIG}"
invert-core analyze-run --run "${RUN}" --config "${CONFIG}"
invert-core summarize-core-v2

echo "Core v2 frozen generalization quadrature complete."
echo "Run: results/core_v2/runs/${RUN}/"
