from __future__ import annotations

from collections import defaultdict
from typing import Any


def _group_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["model"],
        float(row["temperature"]),
        row["class_id"],
        row["task_id"],
        row["requested_pole"],
        row["strip_level"],
    )


def build_entropy_tables(pilot_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in pilot_rows:
        grouped[_group_key(row)].append(row)

    tables: list[dict[str, Any]] = []
    for key, items in sorted(grouped.items()):
        model, temperature, class_id, task_id, pole, strip_level = key
        n_gen = len(items)
        valid = [r for r in items if r.get("behaviorally_valid")]
        recovered = [r for r in valid if r.get("detector_correct")]
        fps = [r["fingerprint_hash"] for r in recovered if r.get("fingerprint_hash")]
        unique = len(set(fps))
        n_valid = len(valid)
        n_rec = len(recovered)
        from invert_discovery.temperature_diversity.metrics import cell_metrics_from_fingerprints

        metrics = cell_metrics_from_fingerprints(
            fps,
            n_generated=n_gen,
            n_valid=n_valid,
            n_recovered=n_rec,
        )
        tables.append(
            {
                "model": model,
                "temperature": temperature,
                "class_id": class_id,
                "task_id": task_id,
                "requested_pole": pole,
                "strip_level": strip_level,
                "n_generated": n_gen,
                "n_valid": n_valid,
                "n_recovered": n_rec,
                "valid_rate": round(metrics.valid_rate, 6),
                "recovery_rate": round(metrics.recovery_rate, 6),
                "unique_fingerprints": metrics.unique_fingerprints,
                "richness": round(metrics.richness, 6),
                "dominance": round(metrics.dominance, 6),
                "shannon_entropy": round(metrics.shannon_entropy, 6),
                "simpson_diversity": round(metrics.simpson_diversity, 6),
            }
        )
    return tables


def build_bootstrap_statistics(
    pilot_rows: list[dict[str, Any]],
    *,
    n_resamples: int = 1000,
) -> list[dict[str, Any]]:
    from invert_discovery.temperature_diversity.metrics import bootstrap_shannon_ci

    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in pilot_rows:
        if row.get("behaviorally_valid") and row.get("detector_correct"):
            grouped[_group_key(row)].append(row)

    stats: list[dict[str, Any]] = []
    index: dict[tuple[Any, ...], float] = {}

    for key, items in sorted(grouped.items()):
        model, temperature, class_id, task_id, pole, strip_level = key
        fps = [r["fingerprint_hash"] for r in items if r.get("fingerprint_hash")]
        point, lo, hi = bootstrap_shannon_ci(fps, n_resamples=n_resamples)
        index[key] = point
        stats.append(
            {
                "model": model,
                "temperature": temperature,
                "class_id": class_id,
                "task_id": task_id,
                "requested_pole": pole,
                "strip_level": strip_level,
                "n_recovered": len(fps),
                "shannon_point": round(point, 6),
                "shannon_ci_low": round(lo, 6),
                "shannon_ci_high": round(hi, 6),
            }
        )

    for row in stats:
        t0_key = (
            row["model"],
            0.0,
            row["class_id"],
            row["task_id"],
            row["requested_pole"],
            row["strip_level"],
        )
        t0_h = index.get(t0_key, 0.0)
        delta = row["shannon_point"] - t0_h
        row["entropy_delta_vs_t0"] = round(delta, 6)
        row["ci_excludes_zero_increase"] = (
            row["temperature"] > 0.0 and row["shannon_ci_low"] > t0_h + 1e-9
        )

    return stats


def build_per_model_summary(entropy_tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in entropy_tables:
        grouped[(row["model"], row["class_id"])].append(row)

    summary: list[dict[str, Any]] = []
    for (model, class_id), rows in sorted(grouped.items()):
        mean_h = sum(r["shannon_entropy"] for r in rows) / max(len(rows), 1)
        max_unique = max((r["unique_fingerprints"] for r in rows), default=0)
        diverse_cells = sum(1 for r in rows if r["unique_fingerprints"] > 1)
        mean_valid = sum(r["valid_rate"] for r in rows) / max(len(rows), 1)
        mean_rec = sum(r["recovery_rate"] for r in rows) / max(len(rows), 1)
        summary.append(
            {
                "model": model,
                "class_id": class_id,
                "cells": len(rows),
                "cells_non_zero_diversity": diverse_cells,
                "max_unique_fingerprints": max_unique,
                "mean_shannon_entropy": round(mean_h, 6),
                "mean_valid_rate": round(mean_valid, 6),
                "mean_recovery_rate": round(mean_rec, 6),
            }
        )
    return summary


def evaluate_go_no_go(
    entropy_tables: list[dict[str, Any]],
    bootstrap_stats: list[dict[str, Any]],
    per_model_summary: list[dict[str, Any]],
) -> dict[str, Any]:
    recovery_stable_threshold = 0.15

    # Criterion 1: C or D diversity increase with stable recovery
    cd_increases: list[dict[str, Any]] = []
    for stat in bootstrap_stats:
        if stat["class_id"] not in {"C", "D"}:
            continue
        if stat["temperature"] < 0.8:
            continue
        if not stat.get("ci_excludes_zero_increase"):
            continue
        ent_row = next(
            (
                r
                for r in entropy_tables
                if (
                    r["model"] == stat["model"]
                    and r["temperature"] == stat["temperature"]
                    and r["class_id"] == stat["class_id"]
                    and r["task_id"] == stat["task_id"]
                    and r["requested_pole"] == stat["requested_pole"]
                    and r["strip_level"] == stat["strip_level"]
                )
            ),
            None,
        )
        t0_row = next(
            (
                r
                for r in entropy_tables
                if (
                    r["model"] == stat["model"]
                    and r["temperature"] == 0.0
                    and r["class_id"] == stat["class_id"]
                    and r["task_id"] == stat["task_id"]
                    and r["requested_pole"] == stat["requested_pole"]
                    and r["strip_level"] == stat["strip_level"]
                )
            ),
            None,
        )
        if ent_row is None or t0_row is None:
            continue
        rec_drop = t0_row["recovery_rate"] - ent_row["recovery_rate"]
        if rec_drop <= recovery_stable_threshold:
            cd_increases.append(stat)

    criterion_1 = len(cd_increases) > 0

    # Criterion 2: monotonic entropy vs temperature on C or D (aggregated per model/class)
    from invert_discovery.temperature_diversity.metrics import is_monotonic_non_decreasing

    monotonic_hits: list[str] = []
    temps = [0.0, 0.4, 0.8]
    for model in sorted({r["model"] for r in entropy_tables}):
        for class_id in ("C", "D"):
            series = []
            for t in temps:
                subset = [
                    r
                    for r in entropy_tables
                    if r["model"] == model and r["class_id"] == class_id and r["temperature"] == t
                ]
                if not subset:
                    continue
                series.append(sum(r["shannon_entropy"] for r in subset) / len(subset))
            if len(series) == 3 and is_monotonic_non_decreasing(series):
                monotonic_hits.append(f"{model}:{class_id}")
    criterion_2 = len(monotonic_hits) > 0

    # Criterion 3: models differ in entropy-temperature curves
    model_curve_diffs: list[dict[str, Any]] = []
    models = sorted({r["model"] for r in entropy_tables})
    if len(models) >= 2:
        m1, m2 = models[0], models[1]
        for class_id in ("C", "D", "E"):
            diffs_at_t = []
            for t in temps:
                h1 = [
                    r["shannon_entropy"]
                    for r in entropy_tables
                    if r["model"] == m1 and r["class_id"] == class_id and r["temperature"] == t
                ]
                h2 = [
                    r["shannon_entropy"]
                    for r in entropy_tables
                    if r["model"] == m2 and r["class_id"] == class_id and r["temperature"] == t
                ]
                if h1 and h2:
                    diffs_at_t.append(abs(sum(h1) / len(h1) - sum(h2) / len(h2)))
            if sum(1 for d in diffs_at_t if d >= 0.2) >= 2:
                model_curve_diffs.append({"class_id": class_id, "models": [m1, m2]})
    criterion_3 = len(model_curve_diffs) > 0

    # Diversity confined to E randomized?
    diverse_cells = [r for r in entropy_tables if r["unique_fingerprints"] > 1]
    diverse_non_e_random = [
        r
        for r in diverse_cells
        if not (r["class_id"] == "E" and r["requested_pole"] == "randomized")
    ]
    only_e_randomized = len(diverse_cells) > 0 and len(diverse_non_e_random) == 0

    go = criterion_1 or criterion_2 or criterion_3

    if only_e_randomized and not go:
        recommended = "no-go"
        reason = "abandon_h01_monoculture_except_e_randomized"
        full_study = False
    elif go:
        recommended = "go"
        reason = (
            "criterion_1_cd_ci_increase"
            if criterion_1
            else "criterion_2_monotonic_entropy"
            if criterion_2
            else "criterion_3_model_curve_divergence"
        )
        full_study = True
    else:
        recommended = "no-go"
        reason = "no_temperature_diversity_signal_on_c_d"
        full_study = False

    return {
        "recommended": recommended,
        "full_study_recommended": full_study,
        "reason": reason,
        "criterion_1_cd_diversity_stable_recovery": criterion_1,
        "criterion_1_examples": len(cd_increases),
        "criterion_2_monotonic_entropy": criterion_2,
        "criterion_2_hits": monotonic_hits,
        "criterion_3_model_curves_differ": criterion_3,
        "criterion_3_examples": model_curve_diffs,
        "only_e_randomized_diversity": only_e_randomized,
        "diverse_cells_total": len(diverse_cells),
        "diverse_cells_non_e_randomized": len(diverse_non_e_random),
    }
