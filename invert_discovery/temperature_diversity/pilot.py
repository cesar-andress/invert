from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from invert_discovery.temperature_diversity.evaluate import evaluate_pilot_artifacts
from invert_discovery.temperature_diversity.generate import generate_pilot_artifacts
from invert_discovery.temperature_diversity.go_no_go import (
    build_bootstrap_statistics,
    build_entropy_tables,
    build_per_model_summary,
    evaluate_go_no_go,
)
from invert_discovery.temperature_diversity.protocol import PILOT_PROTOCOL, PilotProtocol


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({k for row in rows for k in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_pilot_report(
    path: Path,
    *,
    protocol: PilotProtocol,
    pilot_rows: list[dict[str, Any]],
    entropy_tables: list[dict[str, Any]],
    bootstrap_stats: list[dict[str, Any]],
    per_model_summary: list[dict[str, Any]],
    decision: dict[str, Any],
) -> None:
    diverse = [r for r in entropy_tables if r["unique_fingerprints"] > 1]
    top = sorted(
        diverse,
        key=lambda r: (-r["unique_fingerprints"], -r["shannon_entropy"]),
    )[:10]

    paper_strengthen = "unlikely"
    if decision["recommended"] == "go":
        paper_strengthen = "yes — exploratory empirical subsection on temperature vs process diversity"
    elif decision.get("only_e_randomized_diversity"):
        paper_strengthen = "no — would not materially strengthen TOSEM; abandon H01"

    lines = [
        "# H01 Temperature × Process Diversity — Pilot Report",
        "",
        f"**Study ID:** `{protocol.study_id}`",
        f"**Generated (UTC):** {datetime.now(timezone.utc).isoformat()}",
        "",
        "Literature-driven pilot (Lee et al. 2025; Hong et al. 2024). "
        "INVERT is the measuring instrument, not the validation object. "
        "No Core v2 frozen runs or detectors were modified.",
        "",
        "## Preregistered scope",
        "",
        f"- Models: {', '.join(protocol.models)}",
        f"- Temperatures: {protocol.temperatures}",
        f"- Repetitions: {protocol.repetitions}",
        f"- Classes: {', '.join(protocol.classes)}",
        "",
        "## Answers",
        "",
        "### 1. Does temperature actually change process diversity?",
        "",
    ]
    if diverse:
        lines.append(
            f"**Partial / conditional.** {len(diverse)} cells show >1 unique fingerprint "
            f"(of {len(entropy_tables)} cells). See entropy_tables.csv."
        )
        for row in top[:5]:
            lines.append(
                f"- {row['class_id']} {row['task_id']} {row['requested_pole']} "
                f"{row['model']} T={row['temperature']}: "
                f"unique={row['unique_fingerprints']}/{row['n_recovered']} H={row['shannon_entropy']:.4f}"
            )
    else:
        lines.append("**No.** All cells are fingerprint monocultures among recovered artifacts.")

    lines.extend(["", "### 2. Does recovery remain stable?", ""])
    for row in per_model_summary:
        lines.append(
            f"- {row['model']} class {row['class_id']}: "
            f"mean recovery={row['mean_recovery_rate']:.3f}, mean valid={row['mean_valid_rate']:.3f}"
        )

    lines.extend(["", "### 3. Is diversity confined to randomized Class E?", ""])
    lines.append(
        f"- only_e_randomized_diversity: **{decision.get('only_e_randomized_diversity')}** "
        f"({decision.get('diverse_cells_non_e_randomized', 0)} diverse cells outside E:randomized)"
    )

    lines.extend(
        [
            "",
            "### 4. Does perfect recovery mask richer process variation?",
            "",
        ]
    )
    if decision.get("only_e_randomized_diversity"):
        lines.append(
            "Recovery remains high while trace fingerprints stay monoculture on C/D; "
            "variation at E randomized is semantics-aligned, not hidden biodiversity."
        )
    elif diverse:
        lines.append(
            "Some cells show multiple fingerprints despite high recovery — "
            "process variation exists beyond pole label."
        )
    else:
        lines.append("No evidence of hidden variation beyond recovery metrics at this pilot scale.")

    lines.extend(
        [
            "",
            "### 5. Would this materially strengthen the TOSEM paper?",
            "",
            f"**{paper_strengthen}**",
            "",
            "### 6. Should the complete H01 experiment be executed?",
            "",
            f"- **recommended:** `{decision['recommended']}`",
            f"- **full study:** {decision['full_study_recommended']}",
            f"- **reason:** {decision['reason']}",
            "",
            "## Go/no-go criteria",
            "",
            f"- criterion 1 (C/D CI increase, stable recovery): {decision['criterion_1_cd_diversity_stable_recovery']}",
            f"- criterion 2 (monotonic entropy): {decision['criterion_2_monotonic_entropy']} {decision.get('criterion_2_hits', [])}",
            f"- criterion 3 (model curve divergence): {decision['criterion_3_model_curves_differ']}",
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_h01_pilot(
    project_root: Path,
    *,
    protocol: PilotProtocol = PILOT_PROTOCOL,
    generate: bool = True,
    overwrite: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    out = protocol.results_dir(project_root)
    out.mkdir(parents=True, exist_ok=True)

    if generate and not dry_run:
        generate_pilot_artifacts(project_root, protocol=protocol, overwrite=overwrite)
    elif dry_run:
        plan = generate_pilot_artifacts(project_root, protocol=protocol, dry_run=True)
        return {"dry_run": True, "planned_generations": len(plan)}

    pilot_rows = evaluate_pilot_artifacts(project_root, protocol=protocol)
    entropy_tables = build_entropy_tables(pilot_rows)
    bootstrap_stats = build_bootstrap_statistics(pilot_rows)
    per_model_summary = build_per_model_summary(entropy_tables)
    decision = evaluate_go_no_go(entropy_tables, bootstrap_stats, per_model_summary)

    _write_csv(out / "pilot_results.csv", pilot_rows)
    _write_csv(out / "entropy_tables.csv", entropy_tables)
    _write_csv(out / "bootstrap_statistics.csv", bootstrap_stats)
    _write_csv(out / "per_model_summary.csv", per_model_summary)

    payload = {
        "study_id": protocol.study_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "research_question": protocol.research_question,
        "models": list(protocol.models),
        "temperatures": list(protocol.temperatures),
        "artifact_count": len(pilot_rows),
        "decision": decision,
    }
    (out / "H01_GO_NO_GO.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_pilot_report(
        out / "H01_PILOT_REPORT.md",
        protocol=protocol,
        pilot_rows=pilot_rows,
        entropy_tables=entropy_tables,
        bootstrap_stats=bootstrap_stats,
        per_model_summary=per_model_summary,
        decision=decision,
    )
    return payload
