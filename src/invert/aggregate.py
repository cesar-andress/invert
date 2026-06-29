from __future__ import annotations

import csv
import json
from pathlib import Path


def _matches_filters(
    record: dict,
    generator_models: list[str] | None,
    task_ids: list[str] | None,
    judge_models: list[str] | None,
) -> bool:
    if generator_models and record["generator_model"] not in generator_models:
        return False
    if task_ids and record["task_id"] not in task_ids:
        return False
    if judge_models and record["judge_model"] not in judge_models:
        return False
    return True


def run_aggregate(
    data_dir: Path,
    results_dir: Path,
    *,
    generator_models: list[str] | None = None,
    task_ids: list[str] | None = None,
    judge_models: list[str] | None = None,
) -> None:
    recovery_root = data_dir / "recovery"
    results_dir.mkdir(parents=True, exist_ok=True)

    recovery_rows: list[dict] = []
    for path in sorted(recovery_root.rglob("rep_*.json")):
        with open(path, encoding="utf-8") as f:
            record = json.load(f)

        if not _matches_filters(record, generator_models, task_ids, judge_models):
            continue

        manipulated = record["manipulated_dimension"]
        true_value = record["true_value"]
        recovered = record["recovered"].get(manipulated, {})
        recovered_value = recovered.get("value", "")
        confidence = recovered.get("confidence", 0.0)
        correct = recovered_value == true_value

        recovery_rows.append(
            {
                "generator_model": record["generator_model"],
                "judge_model": record["judge_model"],
                "task_id": record["task_id"],
                "manipulated_dimension": manipulated,
                "true_value": true_value,
                "recovered_value": recovered_value,
                "correct": correct,
                "confidence": confidence,
                "rep": record["rep"],
            }
        )

    recovery_csv = results_dir / "recovery.csv"
    fieldnames = [
        "generator_model",
        "judge_model",
        "task_id",
        "manipulated_dimension",
        "true_value",
        "recovered_value",
        "correct",
        "confidence",
        "rep",
    ]
    with open(recovery_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(recovery_rows)

    stats: dict[tuple[str, str], list[bool]] = {}
    for row in recovery_rows:
        key = (row["manipulated_dimension"], row["generator_model"])
        stats.setdefault(key, []).append(row["correct"])

    matrix_rows = []
    for (dimension, model), values in sorted(stats.items()):
        n = len(values)
        accuracy = sum(values) / n if n else 0.0
        matrix_rows.append(
            {"dimension": dimension, "model": model, "accuracy": accuracy, "n": n}
        )

    matrix_csv = results_dir / "identifiability_matrix.csv"
    with open(matrix_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["dimension", "model", "accuracy", "n"])
        writer.writeheader()
        writer.writerows(matrix_rows)
