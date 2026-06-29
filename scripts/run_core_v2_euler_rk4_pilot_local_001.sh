#!/usr/bin/env bash
set -euo pipefail

cd ~/papers/invert/invert

invert-core check-apis --models ollama:qwen2.5-coder:32b,ollama:deepseek-coder-v2:lite
invert-core generate --config configs/core_v2_euler_rk4_pilot_local.yaml --dry-run
invert-core generate --config configs/core_v2_euler_rk4_pilot_local.yaml
invert-core analyze-run --run core_v2_euler_rk4_pilot_local_001

echo "Core v2 Euler/RK4 local pilot complete."
echo "Report: results/core_v2/runs/core_v2_euler_rk4_pilot_local_001/integration_report.md"
