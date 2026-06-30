#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/repo_root.sh"


invert check-apis --models openai,anthropic

invert generate --config configs/pilot.yaml --dry-run

invert generate --config configs/pilot.yaml

invert recover --config configs/pilot.yaml

invert aggregate --run pilot_001

invert plot --run pilot_001

echo "Pilot complete."
echo "Heatmap: results/runs/pilot_001/identifiability_heatmap.png"
