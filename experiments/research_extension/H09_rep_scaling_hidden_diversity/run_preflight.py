#!/usr/bin/env python3
"""Preflight for H09_rep_scaling_hidden_diversity."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from invert_discovery.research_extension.common import (
    check_ollama_models,
    check_path_exists,
    experiment_dir,
    project_root,
    results_dir,
    write_preflight_result,
)

HYPOTHESIS_ID = "H09_rep_scaling_hidden_diversity"


def main() -> int:
    exp = experiment_dir(HYPOTHESIS_ID)
    checks = [
        check_path_exists(exp / "config.yaml", "config.yaml"),
        check_path_exists(exp / "schema.csv", "schema.csv"),
        check_path_exists(exp / "go_no_go.json", "go_no_go.json"),
        check_path_exists(ROOT / "invert_discovery/ecology/fingerprint.py", "fingerprint_module"),
        check_path_exists(
            ROOT / "results/discovery/process_trace_diversity_preflight/ecology_cells.csv",
            "prior_preflight_data",
        ),
    ]
    checks.append(check_ollama_models([
        "ollama:qwen2.5-coder:14b",
        "ollama:devstral:latest",
        "ollama:qwen3-coder:30b",
    ]))
    ok = all(c.get("ok", False) for c in checks)
    notes = [
        "Does increasing N reveal latent diversity without raising temperature?",
        "Preflight only — no full generation in this script.",
        "Estimated generation calls: 1350",
    ]
    write_preflight_result(
        HYPOTHESIS_ID,
        status="ready" if ok else "blocked",
        checks=checks,
        notes=notes,
        estimated_generation_calls=1350,
    )
    print(json.dumps({"status": "ready" if ok else "blocked", "hypothesis": HYPOTHESIS_ID}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
