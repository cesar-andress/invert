#!/usr/bin/env python3
"""Run process trace diversity preflight on frozen Core v2 exports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from invert_discovery.ecology.preflight import run_preflight  # noqa: E402


def main() -> int:
    payload = run_preflight(ROOT)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
