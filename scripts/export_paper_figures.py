#!/usr/bin/env python3
"""Export manuscript supplementary figures from archived Core v2 CSVs (no LLM calls)."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from invert_core.tasks import project_root

FROZEN_RUNS = {
    "Class C (eager/lazy)": "core_v2_generalization_local_eager_lazy_001",
    "Class D (bfs/dfs)": "core_v2_generalization_local_bfs_dfs_001",
    "Class E (det./rand.)": "core_v2_generalization_local_deterministic_randomized_001",
}

STRIP_LEVELS = ["raw", "no_comments", "renamed", "no_imports", "format_normalized"]


def _valid_only_summary_path(run_id: str, root: Path) -> Path:
    prefix = run_id.replace("core_v2_generalization_local_", "").replace("_001", "")
    if prefix == "eager_lazy":
        name = "eager_lazy_valid_only_summary.csv"
    elif prefix == "bfs_dfs":
        name = "bfs_dfs_valid_only_summary.csv"
    elif prefix == "deterministic_randomized":
        name = "deterministic_randomized_valid_only_summary.csv"
    else:
        raise ValueError(f"unsupported run_id: {run_id}")
    return root / "results" / "core_v2" / "runs" / run_id / name


def _aggregate_accuracy(csv_path: Path) -> dict[str, float]:
    totals: dict[str, list[float]] = defaultdict(list)
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            level = row["strip_level"]
            totals[level].append(float(row["valid_detector_accuracy"]))
    return {level: sum(vals) / len(vals) for level, vals in totals.items() if vals}


def export_strip_curves(out_dir: Path, root: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4))
    for label, run_id in FROZEN_RUNS.items():
        csv_path = _valid_only_summary_path(run_id, root)
        acc = _aggregate_accuracy(csv_path)
        ys = [acc.get(level, float("nan")) for level in STRIP_LEVELS]
        ax.plot(STRIP_LEVELS, ys, marker="o", label=label)
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Valid-only recovery accuracy (mean)")
    ax.set_xlabel("Strip level")
    ax.set_title("Frozen generalization: strip-level recovery (Classes C–E)")
    ax.legend(loc="lower left", fontsize=8)
    fig.tight_layout()
    out_path = out_dir / "strip_level_recovery_curves.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def main() -> None:
    root = project_root()
    out_dir = root / "results" / "core_v2" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = export_strip_curves(out_dir, root)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
