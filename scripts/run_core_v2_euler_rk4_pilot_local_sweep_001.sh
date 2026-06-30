#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/repo_root.sh"


invert-core check-apis --models ollama:qwen2.5-coder:32b,ollama:qwen3-coder:30b,ollama:qwen2.5-coder:14b,ollama:devstral:latest,ollama:deepseek-coder-v2:lite
invert-core generate --config configs/core_v2_euler_rk4_pilot_local_sweep.yaml --dry-run
invert-core generate --config configs/core_v2_euler_rk4_pilot_local_sweep.yaml
invert-core analyze-run --run core_v2_euler_rk4_pilot_local_sweep_001

echo "Core v2 Euler/RK4 local model sweep complete."
echo "Report: results/core_v2/runs/core_v2_euler_rk4_pilot_local_sweep_001/integration_report.md"
