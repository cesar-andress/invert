from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from invert_discovery.latent_process_risk.paths import (
    corpus_filters_path,
    lpr_results_dir,
    split_rule_path,
)


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_split_rule() -> dict[str, Any]:
    return load_yaml(split_rule_path())


def load_corpus_filters() -> dict[str, Any]:
    return load_yaml(corpus_filters_path())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_baseline_locked_before_implementation() -> dict[str, Any]:
    lock_path = lpr_results_dir() / "BASELINE_LOCK.json"
    if not lock_path.exists():
        raise RuntimeError("BASELINE_LOCK.json missing — Phase A must complete before implementation")
    lock = load_json(lock_path)
    if not lock.get("implementation_may_begin_after_this_lock"):
        raise RuntimeError("BASELINE_LOCK.json does not authorize implementation")
    if not lock.get("baseline_lock_commit"):
        raise RuntimeError("baseline_lock_commit not set in BASELINE_LOCK.json")
    return lock
