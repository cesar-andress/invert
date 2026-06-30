from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def lpr_results_dir() -> Path:
    return project_root() / "results" / "research_extension" / "LPR"


def split_rule_path() -> Path:
    return lpr_results_dir() / "split_rule.yaml"


def corpus_filters_path() -> Path:
    return lpr_results_dir() / "corpus_filters.yaml"


def baseline_lock_path() -> Path:
    return lpr_results_dir() / "BASELINE_LOCK.json"


def eps_lock_path() -> Path:
    return lpr_results_dir() / "EPS_LOCK.json"
