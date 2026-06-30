from __future__ import annotations

import json
from typing import Any

from invert_discovery.ecology.fingerprint import (
    CLASS_TRACE_FIELDS,
    fingerprint_from_payload,
    normalize_trace_payload,
    trace_payload_from_row,
)


def trace_payload_from_detection(
    class_id: str,
    *,
    evidence: dict[str, Any],
) -> Any | None:
    """Extract bounded trace payload from a detector evidence dict."""

    if class_id == "C":
        return evidence.get("trace")
    if class_id == "D":
        return evidence.get("visit_trace")
    if class_id == "E":
        return evidence.get("traces")
    return None


def fingerprint_from_detection(class_id: str, evidence: dict[str, Any]) -> str | None:
    payload = trace_payload_from_detection(class_id, evidence=evidence)
    return fingerprint_from_payload(payload)


def fingerprint_json(class_id: str, evidence: dict[str, Any]) -> str:
    payload = trace_payload_from_detection(class_id, evidence=evidence)
    if payload is None:
        return ""
    return normalize_trace_payload(payload)


def fingerprint_from_csv_fields(class_id: str, row: dict[str, str]) -> str | None:
    return fingerprint_from_row(row, class_id)


def trace_field_names(class_id: str) -> list[str]:
    return list(CLASS_TRACE_FIELDS.get(class_id, []))
