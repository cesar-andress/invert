#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/repo_root.sh"


invert-core check-apis --models openai,anthropic --strict
invert-core generate --config configs/core_v2_euler_rk4_pilot.yaml --dry-run
invert-core generate --config configs/core_v2_euler_rk4_pilot.yaml
invert-core analyze-run --run core_v2_euler_rk4_pilot_001

echo "Core v2 Euler/RK4 pilot complete."
echo "Report: results/core_v2/runs/core_v2_euler_rk4_pilot_001/integration_report.md"
