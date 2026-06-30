from __future__ import annotations

import hashlib
import json
from typing import Any

# Frozen generalization detection CSVs and their bounded-trace columns.
CLASS_TRACE_FIELDS: dict[str, list[str]] = {
    "B": [
        "coefficient_literals",
        "function_eval_pattern",
        "has_endpoint_half_weights",
        "has_simpson_4_2_pattern",
    ],
    "C": ["trace"],
    "D": ["visit_trace"],
    "E": ["traces"],
}

FROZEN_RUNS: dict[str, dict[str, str]] = {
    "B": {
        "run_id": "core_v2_generalization_local_quadrature_001",
        "csv_name": "quadrature_detection.csv",
    },
    "C": {
        "run_id": "core_v2_generalization_local_eager_lazy_001",
        "csv_name": "eager_lazy_detection.csv",
    },
    "D": {
        "run_id": "core_v2_generalization_local_bfs_dfs_001",
        "csv_name": "bfs_dfs_detection.csv",
    },
    "E": {
        "run_id": "core_v2_generalization_local_deterministic_randomized_001",
        "csv_name": "deterministic_randomized_detection.csv",
    },
}


def _parse_jsonish(value: str) -> Any:
    text = value.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def normalize_trace_payload(payload: Any) -> str:
    """Stable string for hashing bounded trace information."""

    def _norm(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float, str)):
            return value
        if isinstance(value, list):
            return [_norm(item) for item in value]
        if isinstance(value, dict):
            return {str(k): _norm(v) for k, v in sorted(value.items())}
        return str(value)

    normalized = _norm(payload)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def trace_payload_from_row(row: dict[str, str], class_id: str) -> Any | None:
    fields = CLASS_TRACE_FIELDS.get(class_id)
    if not fields:
        return None

    if class_id == "B":
        parts: dict[str, Any] = {}
        for field in fields:
            raw = row.get(field, "")
            if raw == "":
                continue
            if field.startswith("has_"):
                parts[field] = raw.lower() in {"true", "1", "yes"}
            else:
                parts[field] = _parse_jsonish(raw) if ";" in raw or raw.startswith("[") else raw
        return parts or None

    primary = fields[0]
    raw = row.get(primary, "").strip()
    if not raw:
        return None
    return _parse_jsonish(raw)


def fingerprint_from_payload(payload: Any) -> str | None:
    if payload is None:
        return None
    normalized = normalize_trace_payload(payload)
    if normalized in ("null", ""):
        return None
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def fingerprint_from_row(row: dict[str, str], class_id: str) -> str | None:
    payload = trace_payload_from_row(row, class_id)
    return fingerprint_from_payload(payload)
