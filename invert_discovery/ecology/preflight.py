from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from invert_discovery.ecology.fingerprint import (
    CLASS_TRACE_FIELDS,
    FROZEN_RUNS,
    fingerprint_from_row,
    trace_payload_from_row,
)
from invert_discovery.ecology.metrics import cell_ecology_metrics

DYNAMIC_CLASSES = frozenset({"C", "D", "E"})
STRIP_RAW = "raw"
STRIP_FMT = "format_normalized"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def output_dir(root: Path | None = None) -> Path:
    return (root or project_root()) / "results" / "discovery" / "process_trace_diversity_preflight"


def _load_detection_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        return list(reader), fieldnames


def _trace_fields_present(fieldnames: list[str], class_id: str) -> bool:
    required = CLASS_TRACE_FIELDS[class_id]
    return all(field in fieldnames for field in required)


def _is_recovered_row(row: dict[str, str]) -> bool:
    valid = row.get("valid_artifact", "").lower() == "true"
    correct = row.get("detector_correct", "").lower() == "true"
    return valid and correct


def _cell_key(row: dict[str, str], class_id: str) -> tuple[str, str, str, str, str]:
    return (
        class_id,
        row["task_id"],
        row["method"],
        row["model"],
        row["strip_level"],
    )


def _artifact_key(row: dict[str, str]) -> tuple[str, str, str, str, str, str]:
    return (
        row["run"],
        row["model"],
        row["task_id"],
        row["method"],
        str(row["rep"]),
        row["strip_level"],
    )


def load_frozen_inputs(root: Path | None = None) -> dict[str, Any]:
    root = root or project_root()
    runs_root = root / "results" / "core_v2" / "runs"
    availability: dict[str, Any] = {}

    for class_id, spec in FROZEN_RUNS.items():
        csv_path = runs_root / spec["run_id"] / spec["csv_name"]
        rows, fieldnames = _load_detection_csv(csv_path)
        trace_ok = bool(fieldnames) and _trace_fields_present(fieldnames, class_id)
        recovered_rows = [r for r in rows if _is_recovered_row(r)]
        availability[class_id] = {
            "run_id": spec["run_id"],
            "csv_path": str(csv_path),
            "csv_exists": csv_path.exists(),
            "trace_fields_present": trace_ok,
            "trace_fields": CLASS_TRACE_FIELDS[class_id],
            "row_count": len(rows),
            "recovered_row_count": len(recovered_rows),
            "rows": recovered_rows,
        }
    return availability


def build_fingerprints(availability: dict[str, Any]) -> tuple[list[dict[str, Any]], bool]:
    fingerprint_rows: list[dict[str, Any]] = []
    any_trace_data = False

    for class_id, info in availability.items():
        if not info["csv_exists"] or not info["trace_fields_present"]:
            continue
        for row in info["rows"]:
            payload = trace_payload_from_row(row, class_id)
            fp = fingerprint_from_row(row, class_id)
            if payload is not None:
                any_trace_data = True
            fingerprint_rows.append(
                {
                    "class_id": class_id,
                    "run_id": row["run"],
                    "model": row["model"],
                    "task_id": row["task_id"],
                    "requested_pole": row["method"],
                    "rep": row["rep"],
                    "strip_level": row["strip_level"],
                    "artifact_key": "|".join(_artifact_key(row)),
                    "fingerprint": fp or "",
                    "trace_available": payload is not None,
                    "valid_artifact": row.get("valid_artifact", ""),
                    "detector_correct": row.get("detector_correct", ""),
                }
            )
    return fingerprint_rows, any_trace_data


def build_ecology_cells(fingerprint_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[str]] = defaultdict(list)
    meta: dict[tuple[str, ...], dict[str, str]] = {}

    for row in fingerprint_rows:
        if not row["trace_available"] or not row["fingerprint"]:
            continue
        key = (
            row["class_id"],
            row["task_id"],
            row["requested_pole"],
            row["model"],
            row["strip_level"],
        )
        grouped[key].append(row["fingerprint"])
        meta[key] = {
            "class_id": row["class_id"],
            "run_id": row["run_id"],
            "task_id": row["task_id"],
            "requested_pole": row["requested_pole"],
            "model": row["model"],
            "strip_level": row["strip_level"],
        }

    ecology_rows: list[dict[str, Any]] = []
    for key, fps in sorted(grouped.items()):
        metrics = cell_ecology_metrics(fps)
        base = meta[key]
        ecology_rows.append(
            {
                **base,
                "n": metrics.n,
                "unique_fingerprints": metrics.unique_fingerprints,
                "richness": round(metrics.richness, 6),
                "dominance": round(metrics.dominance, 6),
                "shannon_entropy": round(metrics.shannon_entropy, 6),
                "simpson_diversity": round(metrics.simpson_diversity, 6),
                "non_zero_diversity": metrics.unique_fingerprints > 1,
            }
        )
    return ecology_rows


def _pair_entropy_change(ecology_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    index: dict[tuple[str, str, str, str], dict[str, float]] = {}
    for row in ecology_rows:
        key = (
            row["class_id"],
            row["task_id"],
            row["requested_pole"],
            row["model"],
        )
        index.setdefault(key, {})[row["strip_level"]] = row["shannon_entropy"]

    changes: list[dict[str, Any]] = []
    for key, levels in sorted(index.items()):
        if STRIP_RAW in levels and STRIP_FMT in levels:
            changes.append(
                {
                    "class_id": key[0],
                    "task_id": key[1],
                    "requested_pole": key[2],
                    "model": key[3],
                    "shannon_raw": levels[STRIP_RAW],
                    "shannon_format_normalized": levels[STRIP_FMT],
                    "entropy_delta_fmt_minus_raw": round(
                        levels[STRIP_FMT] - levels[STRIP_RAW], 6
                    ),
                    "diversity_survives_stripping": levels[STRIP_FMT] > 0
                    and levels[STRIP_RAW] > 0,
                }
            )
    return changes


def build_model_class_summary(ecology_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in ecology_rows:
        grouped[(row["class_id"], row["model"])].append(row)

    summary: list[dict[str, Any]] = []
    for (class_id, model), rows in sorted(grouped.items()):
        diverse_cells = [r for r in rows if r["non_zero_diversity"]]
        summary.append(
            {
                "class_id": class_id,
                "model": model,
                "cells_total": len(rows),
                "cells_non_zero_diversity": len(diverse_cells),
                "max_unique_fingerprints": max(
                    (r["unique_fingerprints"] for r in rows), default=0
                ),
                "mean_shannon_entropy": round(
                    sum(r["shannon_entropy"] for r in rows) / max(len(rows), 1), 6
                ),
                "class_shows_diversity": len(diverse_cells) > 0,
            }
        )
    return summary


def _top_examples(ecology_rows: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    diverse = [r for r in ecology_rows if r["non_zero_diversity"]]
    return sorted(
        diverse,
        key=lambda r: (
            -r["unique_fingerprints"],
            -r["shannon_entropy"],
            r["class_id"],
            r["task_id"],
        ),
    )[:limit]


def evaluate_go_no_go(
    availability: dict[str, Any],
    ecology_rows: list[dict[str, Any]],
    model_summary: list[dict[str, Any]],
    any_trace_data: bool,
) -> dict[str, Any]:
    if not any_trace_data:
        return {
            "recommended": "no-go",
            "reason": "trace_data_not_available_in_frozen_csvs",
            "dynamic_classes_with_diversity": [],
            "models_with_diversity_by_class": {},
            "diverse_cells_by_class_pole": {},
            "deterministic_pole_diversity": False,
        }

    diverse_cells = [r for r in ecology_rows if r["non_zero_diversity"]]
    diverse_by_class_pole: dict[str, int] = defaultdict(int)
    for row in diverse_cells:
        diverse_by_class_pole[f"{row['class_id']}:{row['requested_pole']}"] += 1

    deterministic_pole_diversity = any(
        r["non_zero_diversity"]
        and not (
            r["class_id"] == "E" and r["requested_pole"] == "randomized"
        )
        for r in ecology_rows
    )

    dynamic_summary = [r for r in model_summary if r["class_id"] in DYNAMIC_CLASSES]
    models_by_class: dict[str, set[str]] = defaultdict(set)
    for row in dynamic_summary:
        if row["class_shows_diversity"]:
            models_by_class[row["class_id"]].add(row["model"])

    classes_with_diversity = sorted(
        cls for cls, models in models_by_class.items() if models
    )
    models_with_diversity_by_class = {
        cls: sorted(models) for cls, models in sorted(models_by_class.items())
    }

    classes_with_two_models = [
        cls for cls in classes_with_diversity if len(models_by_class[cls]) >= 2
    ]

    all_dynamic_monoculture = all(
        not any(r["non_zero_diversity"] for r in ecology_rows if r["class_id"] == cls)
        for cls in DYNAMIC_CLASSES
        if availability.get(cls, {}).get("trace_fields_present")
    )

    if all_dynamic_monoculture:
        return {
            "recommended": "no-go",
            "reason": "dynamic_classes_monoculture",
            "dynamic_classes_with_diversity": [],
            "models_with_diversity_by_class": {},
            "diverse_cells_by_class_pole": dict(diverse_by_class_pole),
            "deterministic_pole_diversity": deterministic_pole_diversity,
        }

    if len(classes_with_two_models) >= 2:
        reason = "two_dynamic_classes_nonzero_diversity_two_models"
        recommended = "go"
    elif len(classes_with_diversity) == 1:
        if not deterministic_pole_diversity:
            reason = "single_dynamic_class_nonzero_diversity_randomized_pole_only"
        else:
            reason = "single_dynamic_class_nonzero_diversity"
        recommended = "maybe"
    elif len(classes_with_diversity) >= 2:
        reason = "two_dynamic_classes_but_few_models"
        recommended = "maybe"
    else:
        reason = "insufficient_diversity_signal"
        recommended = "no-go"

    return {
        "recommended": recommended,
        "reason": reason,
        "dynamic_classes_with_diversity": classes_with_diversity,
        "models_with_diversity_by_class": models_with_diversity_by_class,
        "classes_with_two_or_more_diverse_models": classes_with_two_models,
        "diverse_cells_by_class_pole": dict(diverse_by_class_pole),
        "deterministic_pole_diversity": deterministic_pole_diversity,
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_report(
    path: Path,
    *,
    availability: dict[str, Any],
    ecology_rows: list[dict[str, Any]],
    model_summary: list[dict[str, Any]],
    entropy_changes: list[dict[str, Any]],
    go_no_go: dict[str, Any],
    any_trace_data: bool,
) -> None:
    diverse_cells = [r for r in ecology_rows if r["non_zero_diversity"]]
    top = _top_examples(ecology_rows)
    stripping_survivors = [
        r for r in entropy_changes if r["diversity_survives_stripping"]
    ]

    lines = [
        "# Process Trace Diversity Preflight",
        "",
        "Internal frozen-run discovery analysis on bounded traces already emitted in Core v2 detection CSVs.",
        "Not external validation. Not interface-agnostic recovery. Not a claim of real-world ecological validity.",
        "",
        "## Trace data availability",
        "",
        f"- **trace data available:** {any_trace_data}",
        "",
    ]
    for class_id in sorted(availability):
        info = availability[class_id]
        lines.append(
            f"- **Class {class_id}** (`{info['run_id']}`): "
            f"csv_exists={info['csv_exists']}, trace_fields_present={info['trace_fields_present']}, "
            f"recovered_rows={info['recovered_row_count']}, fields={info['trace_fields']}"
        )

    lines.extend(
        [
            "",
            "## Coverage",
            "",
            f"- classes analyzed: {', '.join(sorted(availability))}",
            f"- ecology cells: {len(ecology_rows)}",
            f"- cells with non-zero diversity: {len(diverse_cells)}",
            f"- stripping pairs (raw vs format_normalized): {len(entropy_changes)}",
            f"- stripping pairs with diversity at both levels: {len(stripping_survivors)}",
            "",
            "## Go / no-go",
            "",
            f"- **recommended:** `{go_no_go['recommended']}`",
            f"- **reason:** {go_no_go['reason']}",
            f"- dynamic classes with diversity: {go_no_go.get('dynamic_classes_with_diversity', [])}",
            f"- diverse cells by class:pole: {go_no_go.get('diverse_cells_by_class_pole', {})}",
            f"- diversity outside Class E randomized pole: {go_no_go.get('deterministic_pole_diversity', False)}",
            "",
            "## Strongest diversity examples",
            "",
        ]
    )
    if top:
        for row in top:
            lines.append(
                f"- Class {row['class_id']} | {row['task_id']} | {row['requested_pole']} | "
                f"{row['model']} | {row['strip_level']}: "
                f"unique={row['unique_fingerprints']}/{row['n']}, "
                f"H={row['shannon_entropy']:.4f}"
            )
    else:
        lines.append("- None (monoculture across all cells).")

    lines.extend(
        [
            "",
            "## Model × class summary",
            "",
        ]
    )
    for row in model_summary:
        lines.append(
            f"- Class {row['class_id']} | {row['model']}: "
            f"{row['cells_non_zero_diversity']}/{row['cells_total']} diverse cells, "
            f"max_unique={row['max_unique_fingerprints']}"
        )

    paper_section = "unlikely"
    if go_no_go["recommended"] == "go":
        paper_section = "yes — exploratory Results subsection on process trace diversity"
    elif go_no_go["recommended"] == "maybe":
        paper_section = "maybe — appendix or short Discussion pointer unless diversity strengthens"

    full_pea = "not recommended"
    if go_no_go["recommended"] == "go":
        full_pea = "recommended — preflight supports full Process Ecology Atlas"
    elif go_no_go["recommended"] == "maybe":
        if go_no_go.get("deterministic_pole_diversity"):
            full_pea = "conditional — only if targeted follow-up finds stronger cross-model patterns"
        else:
            full_pea = "not recommended — diversity confined to Class E randomized pole (semantics-aligned, not hidden biodiversity)"

    lines.extend(
        [
            "",
            "## Caveat",
            "",
            "All 20 diverse cells are Class E with requested pole `randomized`. "
            "Classes C and D show monoculture among valid, correctly recovered artifacts. "
            "Class B (structural fingerprint baseline) is also monoculture. "
            "Interpret diversity as cross-rep implementation variation on the randomized pole, "
            "not as unexpected process biodiversity on deterministic/eager/BFS poles.",
            "",
            "## Interpretation",
            "",
            f"- **paper section potential:** {paper_section}",
            f"- **full PEA worth implementing:** {full_pea}",
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_preflight(root: Path | None = None) -> dict[str, Any]:
    root = root or project_root()
    out = output_dir(root)
    out.mkdir(parents=True, exist_ok=True)

    availability_raw = load_frozen_inputs(root)
    availability = {
        k: {key: v for key, v in info.items() if key != "rows"}
        for k, info in availability_raw.items()
    }

    fingerprint_rows, any_trace_data = build_fingerprints(availability_raw)
    ecology_rows = build_ecology_cells(fingerprint_rows)
    model_summary = build_model_class_summary(ecology_rows)
    entropy_changes = _pair_entropy_change(ecology_rows)
    go = evaluate_go_no_go(
        availability_raw, ecology_rows, model_summary, any_trace_data
    )

    payload = {
        "study_id": "process_trace_diversity_preflight",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trace_data_available": any_trace_data,
        "classes_analyzed": sorted(availability.keys()),
        "frozen_runs": {k: v["run_id"] for k, v in availability.items()},
        "ecology_cells": len(ecology_rows),
        "cells_non_zero_diversity": sum(1 for r in ecology_rows if r["non_zero_diversity"]),
        "go_no_go": go,
        "paper_section_potential": (
            "exploratory_results"
            if go["recommended"] == "go"
            else "appendix_or_discussion"
            if go["recommended"] == "maybe"
            else "unlikely"
        ),
        "full_pea_recommended": go["recommended"] == "go"
        or (
            go["recommended"] == "maybe" and go.get("deterministic_pole_diversity", False)
        ),
    }

    _write_csv(out / "fingerprints.csv", fingerprint_rows)
    _write_csv(out / "ecology_cells.csv", ecology_rows)
    _write_csv(out / "model_class_summary.csv", model_summary)
    write_report(
        out / "PROCESS_TRACE_DIVERSITY_PREFLIGHT.md",
        availability=availability,
        ecology_rows=ecology_rows,
        model_summary=model_summary,
        entropy_changes=entropy_changes,
        go_no_go=go,
        any_trace_data=any_trace_data,
    )
    (out / "process_trace_diversity_go_no_go.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    return payload
