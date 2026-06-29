#!/usr/bin/env python3
"""End-to-end smoke test for INVERT prototype (no API keys required)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

EXPECTED_FILES = [
    RESULTS_DIR / "recovery.csv",
    RESULTS_DIR / "identifiability_matrix.csv",
    RESULTS_DIR / "identifiability_heatmap.png",
]


def run_cmd(args: list[str]) -> None:
    print(f"+ {' '.join(args)}")
    result = subprocess.run(args, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    # Clean prior run artifacts
    for sub in ("raw", "code", "recovery"):
        path = DATA_DIR / sub
        if path.exists():
            shutil.rmtree(path)
    if RESULTS_DIR.exists():
        shutil.rmtree(RESULTS_DIR)

    run_cmd(
        [
            sys.executable,
            "-m",
            "invert.cli",
            "generate",
            "--models",
            "local_stub",
            "--tasks",
            str(PROJECT_ROOT / "data" / "intents" / "tasks.json"),
            "--repetitions",
            "1",
        ]
    )
    run_cmd(
        [
            sys.executable,
            "-m",
            "invert.cli",
            "recover",
            "--judge",
            "local_stub",
            "--models",
            "local_stub",
        ]
    )
    run_cmd([sys.executable, "-m", "invert.cli", "aggregate"])
    run_cmd([sys.executable, "-m", "invert.cli", "plot"])

    missing = [p for p in EXPECTED_FILES if not p.exists()]
    if missing:
        print("Missing expected output files:")
        for p in missing:
            print(f"  - {p}")
        raise SystemExit(1)

    print("Smoke test passed.")
    for p in EXPECTED_FILES:
        print(f"  OK {p}")


if __name__ == "__main__":
    main()
