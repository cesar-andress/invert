from __future__ import annotations

from pathlib import Path
from typing import Any

from invert_core.bfs_dfs_behavioral import run_bfs_dfs_behavioral_oracle
from invert_core.detectors.bfs_dfs import detect_bfs_dfs
from invert_core.detectors.deterministic_randomized import detect_deterministic_randomized
from invert_core.detectors.eager_lazy import detect_eager_lazy
from invert_core.deterministic_randomized_behavioral import run_deterministic_randomized_behavioral_oracle
from invert_core.eager_lazy_behavioral import run_eager_lazy_behavioral_oracle
from invert_core.models import sanitize_model_for_storage

from invert_discovery.temperature_diversity.fingerprint import (
    fingerprint_from_detection,
    fingerprint_json,
)
from invert_discovery.temperature_diversity.generate import _artifact_paths, _load_tasks
from invert_discovery.temperature_diversity.protocol import PILOT_PROTOCOL, PilotProtocol


def _evaluate_code(
    class_id: str,
    code: str,
    task: Any,
    requested_pole: str,
) -> dict[str, Any]:
    if class_id == "C":
        behavioral = run_eager_lazy_behavioral_oracle(code, task)
        parsed = behavioral.parsed
        behavioral_pass = behavioral.behavioral_pass
        valid = parsed and behavioral_pass
        detection = detect_eager_lazy(code, task=task, demand_pattern="partial")
    elif class_id == "D":
        behavioral = run_bfs_dfs_behavioral_oracle(code, task)
        parsed = behavioral.parsed
        behavioral_pass = behavioral.behavioral_pass
        valid = parsed and behavioral_pass
        detection = detect_bfs_dfs(code, task=task)
    elif class_id == "E":
        behavioral = run_deterministic_randomized_behavioral_oracle(code, task)
        parsed = behavioral.parsed
        behavioral_pass = behavioral.behavioral_pass
        valid = parsed and behavioral_pass
        detection = detect_deterministic_randomized(code, task=task, mode="primary")
    else:
        raise ValueError(class_id)

    detected = detection.method
    ambiguous = detected == "ambiguous"
    recovered = valid and not ambiguous and detected == requested_pole
    evidence = detection.evidence
    fp_hash = fingerprint_from_detection(class_id, evidence) or ""
    fp_json = fingerprint_json(class_id, evidence)
    return {
        "behaviorally_valid": valid,
        "parsed": parsed,
        "behavioral_pass": behavioral_pass,
        "detected_pole": detected,
        "detector_correct": recovered,
        "ambiguous": ambiguous,
        "trace_fingerprint": fp_json,
        "fingerprint_hash": fp_hash,
        "reason": evidence.get("reason", ""),
    }


def evaluate_pilot_artifacts(
    project_root: Path,
    *,
    protocol: PilotProtocol = PILOT_PROTOCOL,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    task_cache: dict[str, dict[str, Any]] = {}

    for class_id in protocol.classes:
        tasks = _load_tasks(protocol, project_root, class_id)
        task_cache[class_id] = {t.task_id: t for t in tasks}
        poles = protocol.classes[class_id]["poles"]

        for model in protocol.models:
            storage = sanitize_model_for_storage(model)
            class_root = protocol.data_root(project_root) / storage / class_id
            if not class_root.exists():
                continue
            for task_id in protocol.classes[class_id]["task_ids"]:
                task = task_cache[class_id][task_id]
                for pole in poles:
                    for temperature in protocol.temperatures:
                        for rep in range(1, protocol.repetitions + 1):
                            _, code_path = _artifact_paths(
                                protocol,
                                project_root=project_root,
                                model=model,
                                class_id=class_id,
                                task_id=task_id,
                                pole=pole,
                                temperature=temperature,
                                rep=rep,
                            )
                            if not code_path.exists():
                                continue
                            code = code_path.read_text(encoding="utf-8")
                            for strip_level in protocol.strip_levels:
                                result = _evaluate_code(class_id, code, task, pole)
                                rows.append(
                                    {
                                        "study_id": protocol.study_id,
                                        "model": model,
                                        "temperature": temperature,
                                        "class_id": class_id,
                                        "task_id": task_id,
                                        "requested_pole": pole,
                                        "rep": rep,
                                        "strip_level": strip_level,
                                        **result,
                                    }
                                )
    return rows
