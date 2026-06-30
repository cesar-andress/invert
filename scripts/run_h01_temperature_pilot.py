#!/usr/bin/env python3
"""Run H01 temperature × process diversity pilot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from invert_discovery.temperature_diversity.pilot import run_h01_pilot  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Count planned generations only")
    parser.add_argument("--evaluate-only", action="store_true", help="Skip generation")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate existing artifacts")
    args = parser.parse_args()

    payload = run_h01_pilot(
        ROOT,
        generate=not args.evaluate_only,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
