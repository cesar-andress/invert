#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/repo_root.sh"


MODELS="ollama:qwen2.5-coder:14b,ollama:qwen2.5-coder:32b,ollama:qwen3-coder:30b,ollama:devstral:latest"
CONFIG="configs/core_v2_generalization_local_bfs_dfs.yaml"
RUN="core_v2_generalization_local_bfs_dfs_001"

invert-core check-apis --models "${MODELS}"
invert-core generate --config "${CONFIG}" --dry-run
invert-core generate --config "${CONFIG}"
invert-core analyze-run --run "${RUN}" --config "${CONFIG}"
invert-core summarize-core-v2

echo "Core v2 frozen generalization bfs/dfs complete."
echo "Run: results/core_v2/runs/${RUN}/"
