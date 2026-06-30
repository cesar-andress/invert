#!/usr/bin/env python3
"""HumanEval+ output-stability pilot (invert_external; not Class E validation)."""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
os.environ["PYTHONHASHSEED"] = "0"

from evalplus.data import get_human_eval_plus  # noqa: E402

from invert_core.models import OllamaClient, parse_ollama_model  # noqa: E402
from invert_external.detectors.output_stability import (  # noqa: E402
    OutputStabilityProtocol,
    analyze_output_stability,
    detector_sha256,
)
from invert_external.harness.humaneval_plus import (  # noqa: E402
    bundle_and_validator,
    evalplus_functionally_valid,
    full_code,
    oracle_for_task,
)

PILOT_TASKS = 30
MODEL_SPEC = "ollama:qwen2.5-coder:14b"
PROTOCOL = OutputStabilityProtocol(run_count=10, timeout_sec=2.0)
OUT_RESULTS = ROOT / "external_variability_pilot_results.csv"
OUT_SUMMARY = ROOT / "external_variability_pilot_summary.csv"
OUT_REPORT = ROOT / "EXTERNAL_VARIABILITY_PILOT_REPORT.md"
OUT_GO = ROOT / "external_variability_pilot_go_no_go.json"
ARTIFACT_DIR = ROOT / "results" / "external_variability" / "pilot_v2"


def _prompt(problem: dict[str, Any]) -> str:
    return (
        "Complete the following Python function. Return only the function implementation.\n\n"
        f"{problem['prompt']}"
    )


def _analyze_row(
    *,
    task_id: str,
    source_group: str,
    model_id: str,
    artifact_id: str,
    code: str,
    problem: dict[str, Any],
    oracle: dict[str, Any],
    generation_sec: float | None = None,
) -> dict[str, Any]:
    bundle, validator = bundle_and_validator(problem, oracle)
    valid, gate_reason = evalplus_functionally_valid(problem, code, oracle)
    result = analyze_output_stability(
        code,
        artifact_id=artifact_id,
        entry_point=problem["entry_point"],
        bundles=[bundle],
        protocol=PROTOCOL,
        validators={bundle.bundle_id: validator},
        functionally_valid=valid,
        validation_error=gate_reason or None,
    )
    bundle_result = result.bundle_results[0] if result.bundle_results else None
    row = {
        "study_id": "RQ-EXT-E",
        "dataset": "humaneval_plus_v1",
        "task_id": task_id,
        "model_id": model_id,
        "source_group": source_group,
        "artifact_id": artifact_id,
        "label": result.label,
        "functionally_valid": valid,
        "unique_output_hash_count": bundle_result.unique_output_hash_count
        if bundle_result
        else 0,
        "pass_count": bundle_result.pass_count if bundle_result else 0,
        "fail_count": bundle_result.fail_count if bundle_result else 0,
        "timeout_count": bundle_result.timeout_count if bundle_result else 0,
        "error_count": bundle_result.error_count if bundle_result else 0,
        "ambiguous_count": bundle_result.ambiguous_count if bundle_result else 0,
        "validation_error": gate_reason,
        "run_count": PROTOCOL.run_count,
        "detector_sha256": detector_sha256(),
        "detector_module": "invert_external.detectors.output_stability",
    }
    if generation_sec is not None:
        row["generation_sec"] = generation_sec
    return row


def main() -> int:
    t0 = time.time()
    problems = get_human_eval_plus()
    task_ids = sorted(problems.keys())[:PILOT_TASKS]

    ollama_model = parse_ollama_model(MODEL_SPEC)
    if ollama_model is None:
        raise SystemExit(f"bad model spec: {MODEL_SPEC}")
    client = OllamaClient(model=ollama_model, temperature=0.0, max_retries=2)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    failures: list[str] = []

    for task_id in task_ids:
        problem = problems[task_id]
        oracle = oracle_for_task(problem)
        ref_code = problem["prompt"] + problem["canonical_solution"]
        rows.append(
            _analyze_row(
                task_id=task_id,
                source_group="reference",
                model_id="canonical",
                artifact_id=f"ref_{task_id.replace('/', '_')}",
                code=ref_code,
                problem=problem,
                oracle=oracle,
            )
        )

        gen_prompt = _prompt(problem)
        t_gen = time.time()
        try:
            raw = client.generate(gen_prompt)
            code = full_code(problem["prompt"], raw)
            (ARTIFACT_DIR / f"{task_id.replace('/', '_')}.json").write_text(
                json.dumps({"prompt": gen_prompt, "raw": raw, "code": code}, indent=2),
                encoding="utf-8",
            )
            rows.append(
                _analyze_row(
                    task_id=task_id,
                    source_group="local_llm",
                    model_id=MODEL_SPEC,
                    artifact_id=f"gen_{task_id.replace('/', '_')}",
                    code=code,
                    problem=problem,
                    oracle=oracle,
                    generation_sec=round(time.time() - t_gen, 2),
                )
            )
        except Exception as exc:
            failures.append(f"generation {task_id}: {exc}")
            rows.append(
                {
                    "study_id": "RQ-EXT-E",
                    "dataset": "humaneval_plus_v1",
                    "task_id": task_id,
                    "model_id": MODEL_SPEC,
                    "source_group": "local_llm",
                    "artifact_id": f"gen_{task_id.replace('/', '_')}",
                    "label": "error",
                    "functionally_valid": False,
                    "unique_output_hash_count": 0,
                    "pass_count": 0,
                    "fail_count": 0,
                    "timeout_count": 0,
                    "error_count": 1,
                    "ambiguous_count": 0,
                    "validation_error": str(exc),
                    "run_count": PROTOCOL.run_count,
                    "detector_sha256": detector_sha256(),
                    "detector_module": "invert_external.detectors.output_stability",
                    "generation_sec": round(time.time() - t_gen, 2),
                }
            )

    fieldnames = sorted({k for row in rows for k in row.keys()})
    with OUT_RESULTS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    generated = [r for r in rows if r["source_group"] == "local_llm"]
    reference = [r for r in rows if r["source_group"] == "reference"]
    valid_gen = [r for r in generated if r.get("functionally_valid")]

    def count(items: list[dict], label: str) -> int:
        return sum(1 for r in items if r.get("label") == label)

    metrics = {
        "tasks_attempted": len(task_ids),
        "generated_n": len(generated),
        "valid_n": len(valid_gen),
        "invalid_n": len(generated) - len(valid_gen),
        "stable_n": count(valid_gen, "stable"),
        "variable_n": count(valid_gen, "variable"),
        "flaky_invalid_n": count(valid_gen, "flaky_invalid"),
        "timeout_n": count(rows, "timeout"),
        "error_n": count(rows, "error"),
        "ambiguous_n": count(rows, "ambiguous"),
        "reference_n": len(reference),
        "reference_stable_n": count(reference, "stable"),
    }
    variable_rate = metrics["variable_n"] / max(metrics["valid_n"], 1)
    invalid_rate = metrics["invalid_n"] / max(metrics["generated_n"], 1)
    ref_stable_rate = metrics["reference_stable_n"] / max(metrics["reference_n"], 1)

    if ref_stable_rate < 0.95:
        decision = "revise-plan"
        full_study = False
        paper_now = "artifact-only"
        reason = "reference_harness_unstable"
    elif metrics["ambiguous_n"] > 0 and metrics["valid_n"] == 0:
        decision = "no-go"
        full_study = False
        paper_now = "artifact-only"
        reason = "detector_or_harness_ambiguous"
    elif invalid_rate > 0.5:
        decision = "revise-plan"
        full_study = False
        paper_now = "artifact-only"
        reason = "harness_or_generation_dominated_invalid"
    elif variable_rate >= 0.02:
        decision = "go"
        full_study = True
        paper_now = "appendix-exploratory"
        reason = "variable_rate_gte_2pct"
    elif metrics["valid_n"] > 0 and variable_rate < 0.02:
        decision = "revise-plan"
        full_study = False
        paper_now = "artifact-only"
        reason = "low_prevalence_null_finding"
    else:
        decision = "revise-plan"
        full_study = False
        paper_now = "artifact-only"
        reason = "insufficient_valid_artifacts"

    elapsed = round(time.time() - t0, 1)
    gen_sec = sum(float(r.get("generation_sec", 0) or 0) for r in generated)

    summary_rows = [
        {"metric": k, "value": v} for k, v in metrics.items()
    ] + [
        {"metric": "variable_rate_valid", "value": round(variable_rate, 4)},
        {"metric": "invalid_rate_generated", "value": round(invalid_rate, 4)},
        {"metric": "reference_stable_rate", "value": round(ref_stable_rate, 4)},
        {"metric": "elapsed_sec", "value": elapsed},
        {"metric": "generation_sec_total", "value": round(gen_sec, 1)},
    ]
    with OUT_SUMMARY.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows(summary_rows)

    go = {
        "study_id": "RQ-EXT-E",
        "pilot_date": datetime.now(timezone.utc).isoformat(),
        "recommended": decision,
        "full_study_recommended": full_study,
        "paper_placement": paper_now,
        "reason": reason,
        "metrics": metrics,
        "variable_rate_among_valid": round(variable_rate, 4),
        "model": MODEL_SPEC,
        "dataset": "humaneval_plus_v1",
        "detector_module": "invert_external.detectors.output_stability",
        "detector_sha256": detector_sha256(),
        "uses_invert_api": False,
        "unexpected_failures": failures,
        "elapsed_sec": elapsed,
    }
    OUT_GO.write_text(json.dumps(go, indent=2) + "\n", encoding="utf-8")

    report = [
        "# External Variability Pilot Report (output-stability)",
        "",
        f"**Detector:** `invert_external.detectors.output_stability`",
        f"**SHA256:** `{detector_sha256()}`",
        f"**Dataset:** HumanEval+ ({PILOT_TASKS} tasks)",
        f"**Model:** `{MODEL_SPEC}`",
        "",
        "## Summary",
        "",
    ]
    for item in summary_rows:
        report.append(f"- {item['metric']}: {item['value']}")
    report.extend(
        [
            "",
            "## Decision",
            "",
            f"- **recommended:** `{decision}`",
            f"- **full study:** {full_study}",
            f"- **paper placement:** {paper_now}",
            f"- **reason:** {reason}",
            "",
            "This pilot is **not** Class E external validation.",
            "",
        ]
    )
    OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(go, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
