#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/repo_root.sh"


invert-core check-apis --models ollama:qwen2.5-coder:14b,ollama:qwen2.5-coder:32b,ollama:qwen3-coder:30b,ollama:devstral:latest
invert-core generate --config configs/core_v2_eager_lazy_pilot_local.yaml --dry-run
invert-core generate --config configs/core_v2_eager_lazy_pilot_local.yaml
invert-core analyze-run --run core_v2_eager_lazy_pilot_local_001
invert-core summarize-core-v2

echo "Core v2 eager/lazy pilot complete."
echo "Report: results/core_v2/runs/core_v2_eager_lazy_pilot_local_001/eager_lazy_report.md"
