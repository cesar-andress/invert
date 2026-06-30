from __future__ import annotations

import hashlib
import math
from typing import Any

from invert_discovery.latent_process_risk.config import load_split_rule


def _stable_test_pairs(inputs: list[str], outputs: list[str]) -> list[tuple[str, str]]:
    if len(inputs) != len(outputs):
        raise ValueError("inputs and outputs length mismatch")
    return list(zip(inputs, outputs, strict=True))


def assign_public_withheld_indices(num_tests: int, rule: dict[str, Any] | None = None) -> tuple[list[int], list[int]]:
    """Deterministic public/withheld partition per split_rule.yaml."""
    if num_tests < 1:
        raise ValueError("num_tests must be positive")
    rule = rule or load_split_rule()
    frac = float(rule["partition"]["public_fraction"])
    n_public = math.floor(frac * num_tests)
    public = list(range(n_public))
    withheld = list(range(n_public, num_tests))
    mins = rule["partition"]["minimum_counts_after_partition"]
    if len(public) < int(mins["public_tests_min"]) or len(withheld) < int(mins["withheld_tests_min"]):
        raise ValueError("SPLIT_INSUFFICIENT_COUNTS")
    return public, withheld


def statement_fingerprint(statement: str) -> str:
    normalized = statement.encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def split_manifest_hash(inputs: list[str], outputs: list[str]) -> str:
    pairs = _stable_test_pairs(inputs, outputs)
    payload = "\n".join(f"{i}\t{hashlib.sha256(inp.encode()).hexdigest()}" for i, (inp, _) in enumerate(pairs))
    return hashlib.sha256(payload.encode()).hexdigest()
