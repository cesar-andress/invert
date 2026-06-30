#!/usr/bin/env python3
"""Phase-1 pilot for external variability study (RQ-EXT-E). Smoke + HumanEval+ only."""

from __future__ import annotations

import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evalplus.data import get_human_eval_plus  # noqa: E402
from evalplus.eval import FAIL, PASS, untrusted_check  # noqa: E402
from evalplus.gen.util import trusted_exec  # noqa: E402
from invert.generate import extract_code  # noqa: E402
from invert_core.external.external_variability_detector import (  # noqa: E402
    ExternalVariabilityProtocol,
    InputBundle,
    analyze_external_variability,
    detector_sha256,
    load_protocol,
)
from invert_core.models import OllamaClient, parse_ollama_model  # noqa: E402

PILOT_TASK_COUNT = 8
MODEL_SPEC = "ollama:qwen2.5-coder:14b"
CONFIG_PATH = ROOT / "configs" / "external_variability_protocol.yaml"
OUT_CSV = ROOT / "external_variability_pilot_results.csv"
OUT_REPORT = ROOT / "EXTERNAL_VARIABILITY_PILOT_REPORT.md"
OUT_GO_NO_GO = ROOT / "external_variability_pilot_go_no_go.json"
ARTIFACT_DIR = ROOT / "results" / "external_variability" / "pilot"


def _select_tasks(problems: dict[str, Any], n: int) -> list[str]:
    return sorted(problems.keys())[:n]


def _build_prompt(problem: dict[str, Any]) -> str:
    return (
        "Complete the following Python function. Return only the function implementation.\n\n"
        f"{problem['prompt']}"
    )


def _build_full_code(prompt: str, completion: str) -> str:
    body = extract_code(completion)
    if body.lstrip().startswith("def "):
        return body
    return prompt + body


def _oracle_for_task(problem: dict[str, Any]) -> dict[str, Any]:
    code = problem["prompt"] + problem["canonical_solution"]
    entry = problem["entry_point"]
    base_out, base_time = trusted_exec(
        code, problem["base_input"], entry, record_time=True
    )
    plus_out, plus_time = trusted_exec(
        code, problem["plus_input"], entry, record_time=True
    )
    return {
        "base": base_out,
        "base_time": base_time,
        "plus": plus_out,
        "plus_time": plus_time,
    }


def _outputs_match(output: Any, expected: Any, atol: float) -> bool:
    if output == expected:
        return True
    try:
        if atol == 0 and isinstance(expected, float):
            atol = 1e-6
        if atol != 0:
            np.testing.assert_allclose(output, expected, rtol=1e-7, atol=atol)
            return True
    except Exception:
        return False
    return False


def _evalplus_one_shot_pass(
    problem: dict[str, Any], code: str, oracle: dict[str, Any]
) -> tuple[bool, str]:
    status, _ = untrusted_check(
        "humaneval",
        code,
        problem["plus_input"],
        problem["entry_point"],
        oracle["plus"],
        problem["atol"],
        oracle["plus_time"],
        fast_check=True,
    )
    if status == PASS:
        return True, ""
    return False, status


def _bundle_and_validator(
    problem: dict[str, Any], oracle: dict[str, Any]
) -> tuple[InputBundle, Callable[[Any], bool]]:
    inp = problem["base_input"][0]
    expected = oracle["base"][0]
    atol = float(problem["atol"])

    def validator(output: Any) -> bool:
        return _outputs_match(output, expected, atol)

    bundle = InputBundle(
        bundle_id="base_input_0",
        args=tuple(inp),
        sort_output_for_comparison=False,
    )
    return bundle, validator


def _analyze_artifact(
    *,
    artifact_id: str,
    source_group: str,
    model_id: str,
    task_id: str,
    code: str,
    problem: dict[str, Any],
    oracle: dict[str, Any],
    protocol: ExternalVariabilityProtocol,
) -> dict[str, Any]:
    one_shot, gate_reason = _evalplus_one_shot_pass(problem, code, oracle)
    bundle, validator = _bundle_and_validator(problem, oracle)
    result = analyze_external_variability(
        code,
        artifact_id=artifact_id,
        entry_point=problem["entry_point"],
        bundles=[bundle],
        protocol=protocol,
        validators={bundle.bundle_id: validator},
    )
    bundle_result = result.bundle_results[0] if result.bundle_results else None
    return {
        "study_id": "RQ-EXT-E",
        "dataset": "humaneval_plus_v1",
        "task_id": task_id,
        "model_id": model_id,
        "source_group": source_group,
        "artifact_id": artifact_id,
        "entry_point": problem["entry_point"],
        "bundle_id": bundle.bundle_id,
        "one_shot_pass": one_shot,
        "externally_valid": result.externally_valid and one_shot,
        "one_shot_pass_and_variable": one_shot
        and result.aggregate_label == "variable",
        "one_shot_pass_and_flaky": one_shot
        and result.aggregate_label == "flaky_invalid",
        "variability_label": result.aggregate_label
        if one_shot
        else "invalid_functional",
        "unique_output_hash_count": bundle_result.unique_output_hash_count
        if bundle_result
        else 0,
        "pass_count": bundle_result.pass_count if bundle_result else 0,
        "fail_count": bundle_result.fail_count if bundle_result else 0,
        "timeout_count": bundle_result.timeout_count if bundle_result else 0,
        "error_count": bundle_result.error_count if bundle_result else 0,
        "ambiguous_count": bundle_result.ambiguous_count if bundle_result else 0,
        "run_count": protocol.run_count,
        "timeout_sec": protocol.timeout_sec,
        "validation_error": gate_reason or result.validation_error or "",
        "detector_sha256": detector_sha256(),
        "protocol_version": "1.0",
    }


def main() -> int:
    t0 = time.time()
    protocol = load_protocol(CONFIG_PATH)
    problems = get_human_eval_plus()
    task_ids = _select_tasks(problems, PILOT_TASK_COUNT)

    ollama_model = parse_ollama_model(MODEL_SPEC)
    if ollama_model is None:
        raise SystemExit(f"Invalid model spec: {MODEL_SPEC}")
    client = OllamaClient(model=ollama_model, temperature=0.0, max_retries=2)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    failures: list[str] = []

    for task_id in task_ids:
        problem = problems[task_id]
        oracle = _oracle_for_task(problem)

        ref_code = problem["prompt"] + problem["canonical_solution"]
        rows.append(
            _analyze_artifact(
                artifact_id=f"reference_{task_id.replace('/', '_')}",
                source_group="reference",
                model_id="canonical",
                task_id=task_id,
                code=ref_code,
                problem=problem,
                oracle=oracle,
                protocol=protocol,
            )
        )

        gen_prompt = _build_prompt(problem)
        t_gen = time.time()
        try:
            raw = client.generate(gen_prompt)
        except Exception as exc:
            failures.append(f"generation_failed {task_id}: {exc}")
            rows.append(
                {
                    "study_id": "RQ-EXT-E",
                    "dataset": "humaneval_plus_v1",
                    "task_id": task_id,
                    "model_id": MODEL_SPEC,
                    "source_group": "local_llm",
                    "artifact_id": f"gen_{task_id.replace('/', '_')}",
                    "entry_point": problem["entry_point"],
                    "bundle_id": "",
                    "one_shot_pass": False,
                    "externally_valid": False,
                    "one_shot_pass_and_variable": False,
                    "one_shot_pass_and_flaky": False,
                    "variability_label": "generation_failed",
                    "unique_output_hash_count": 0,
                    "pass_count": 0,
                    "fail_count": 0,
                    "timeout_count": 0,
                    "error_count": 0,
                    "ambiguous_count": 0,
                    "run_count": protocol.run_count,
                    "timeout_sec": protocol.timeout_sec,
                    "validation_error": str(exc),
                    "detector_sha256": detector_sha256(),
                    "protocol_version": "1.0",
                    "generation_sec": round(time.time() - t_gen, 2),
                }
            )
            continue

        gen_path = ARTIFACT_DIR / f"{task_id.replace('/', '_')}.json"
        gen_path.write_text(
            json.dumps({"prompt": gen_prompt, "raw": raw}, indent=2) + "\n",
            encoding="utf-8",
        )
        full_code = _build_full_code(problem["prompt"], raw)
        row = _analyze_artifact(
            artifact_id=f"gen_{task_id.replace('/', '_')}",
            source_group="local_llm",
            model_id=MODEL_SPEC,
            task_id=task_id,
            code=full_code,
            problem=problem,
            oracle=oracle,
            protocol=protocol,
        )
        row["generation_sec"] = round(time.time() - t_gen, 2)
        rows.append(row)

    fieldnames = list(rows[0].keys()) if rows else []
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    generated = [r for r in rows if r["source_group"] == "local_llm"]
    reference = [r for r in rows if r["source_group"] == "reference"]
    valid = [r for r in generated if r.get("one_shot_pass")]
    parsed_n = len(generated)

    def _count(label: str, items: list[dict[str, Any]]) -> int:
        return sum(1 for r in items if r.get("variability_label") == label)

    metrics = {
        "task_count": len(task_ids),
        "generated_n": parsed_n,
        "parsed_n": parsed_n,
        "valid_n": len(valid),
        "invalid_n": parsed_n - len(valid),
        "stable_n": _count("stable", valid),
        "variable_n": _count("variable", valid),
        "flaky_invalid_n": _count("flaky_invalid", valid),
        "ambiguous_n": _count("ambiguous", rows),
        "timeout_n": _count("timeout", rows),
        "error_n": _count("error", rows),
        "reference_stable_n": _count("stable", reference),
        "reference_n": len(reference),
    }

    elapsed = round(time.time() - t0, 1)
    gen_secs = sum(float(r.get("generation_sec", 0)) for r in generated)

    ref_stable_rate = metrics["reference_stable_n"] / max(metrics["reference_n"], 1)
    harness_ok = ref_stable_rate >= 0.95

    if not harness_ok:
        decision = "revise-plan"
        scaling = False
        paper_worth = False
        reason = "reference_stability_below_95_percent"
    elif metrics["ambiguous_n"] > 0 and metrics["valid_n"] == 0:
        decision = "revise-plan"
        scaling = False
        paper_worth = False
        reason = "ambiguous_or_harness_issues"
    elif metrics["variable_n"] > 0 or metrics["flaky_invalid_n"] > 0:
        decision = "go"
        scaling = True
        paper_worth = True
        reason = "variability_or_flakiness_observed_in_valid_artifacts"
    elif metrics["valid_n"] > 0 and metrics["stable_n"] == metrics["valid_n"]:
        decision = "revise-plan"
        scaling = True
        paper_worth = True
        reason = "null_prevalence_informative_but_scale_for_confidence_intervals"
    elif metrics["valid_n"] == 0:
        decision = "revise-plan"
        scaling = False
        paper_worth = False
        reason = "high_invalid_rate_revise_generation_harness"
    else:
        decision = "revise-plan"
        scaling = False
        paper_worth = False
        reason = "mixed_outcomes_review"

    go_payload = {
        "study_id": "RQ-EXT-E",
        "pilot_date": datetime.now(timezone.utc).isoformat(),
        "recommended": decision,
        "scaling_recommended": scaling,
        "worth_adding_to_paper": paper_worth,
        "reason": reason,
        "metrics": metrics,
        "model": MODEL_SPEC,
        "detector_sha256": detector_sha256(),
        "harness_sanity_reference_stable_rate": round(ref_stable_rate, 4),
        "elapsed_sec": elapsed,
        "generation_sec_total": round(gen_secs, 1),
        "cost_usd": 0.0,
        "unexpected_failures": failures,
        "results_csv": str(OUT_CSV.relative_to(ROOT)),
    }
    OUT_GO_NO_GO.write_text(json.dumps(go_payload, indent=2) + "\n", encoding="utf-8")

    report_lines = [
        "# External Variability Pilot Report",
        "",
        f"**Date:** {go_payload['pilot_date']}",
        f"**Model:** `{MODEL_SPEC}`",
        f"**Tasks:** {metrics['task_count']} (HumanEval+)",
        f"**Detector SHA256:** `{detector_sha256()}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|--------|------:|",
    ]
    for key, val in metrics.items():
        report_lines.append(f"| {key} | {val} |")
    report_lines.extend(
        [
            "",
            "## Reference solutions",
            "",
            f"- Stable: {metrics['reference_stable_n']} / {metrics['reference_n']}",
            f"- Reference stable rate: {ref_stable_rate:.1%}",
            "",
            "## Generated artifacts (valid only)",
            "",
        ]
    )
    for r in valid:
        report_lines.append(
            f"- `{r['task_id']}`: `{r['variability_label']}` "
            f"(unique_hashes={r['unique_output_hash_count']})"
        )
    if not valid:
        report_lines.append("- None passed EvalPlus one-shot gate.")
    report_lines.extend(
        [
            "",
            "## Runtime",
            "",
            f"- Total elapsed: {elapsed}s",
            f"- Generation (local Ollama): {gen_secs:.1f}s",
            f"- Cost: $0 (local)",
            "",
            "## Unexpected failures",
            "",
        ]
    )
    if failures:
        report_lines.extend(f"- {f}" for f in failures)
    else:
        report_lines.append("- None")
    report_lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- **Recommendation:** `{decision}`",
            f"- **Scaling recommended:** {scaling}",
            f"- **Worth adding to paper (exploratory):** {paper_worth}",
            f"- **Reason:** {reason}",
            "",
        ]
    )
    OUT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(json.dumps(go_payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
