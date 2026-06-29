from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

from invert.schemas import DIMENSION_NAMES


def run_plot(results_dir: Path) -> None:
    matrix_path = results_dir / "identifiability_matrix.csv"
    if not matrix_path.exists():
        raise FileNotFoundError(f"Missing {matrix_path}. Run 'invert aggregate' first.")

    rows: list[dict[str, str | float | int]] = []
    with open(matrix_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    models = sorted({str(r["model"]) for r in rows})
    dimensions = [d for d in DIMENSION_NAMES if any(str(r["dimension"]) == d for r in rows)]
    if not dimensions:
        dimensions = sorted({str(r["dimension"]) for r in rows})

    lookup: dict[tuple[str, str], float] = {}
    for r in rows:
        lookup[(str(r["dimension"]), str(r["model"]))] = float(r["accuracy"])

    data = []
    for dim in dimensions:
        row = [lookup.get((dim, model), float("nan")) for model in models]
        data.append(row)

    fig, ax = plt.subplots(figsize=(max(6, len(models) * 1.5), max(6, len(dimensions) * 0.6)))
    im = ax.imshow(data, aspect="auto", vmin=0.0, vmax=1.0, cmap="RdYlGn")

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, rotation=45, ha="right")
    ax.set_yticks(range(len(dimensions)))
    ax.set_yticklabels(dimensions)
    ax.set_xlabel("Generator model")
    ax.set_ylabel("Intent dimension")
    ax.set_title("Identifiability heatmap (manipulated dimension recovery accuracy)")

    for i, dim in enumerate(dimensions):
        for j, model in enumerate(models):
            val = lookup.get((dim, model), float("nan"))
            if val == val:  # not nan
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8)

    fig.colorbar(im, ax=ax, label="Accuracy")
    fig.tight_layout()

    out_path = results_dir / "identifiability_heatmap.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
