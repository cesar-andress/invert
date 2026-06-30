from __future__ import annotations

import hashlib
import json
import math
import signal
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, Sequence

StabilityLabel = Literal[
    "stable",
    "variable",
    "invalid",
    "flaky_invalid",
    "timeout",
    "error",
    "ambiguous",
]

RunStatus = Literal["pass", "fail", "timeout", "error", "ambiguous"]


@dataclass(frozen=True)
class InputBundle:
    bundle_id: str
    args: tuple[Any, ...] = ()
    sort_output_for_comparison: bool = False


@dataclass(frozen=True)
class OutputStabilityProtocol:
    run_count: int = 10
    timeout_sec: float = 2.0
    normalize_whitespace: bool = True
    max_output_chars: int = 65536


@dataclass
class RunRecord:
    run_index: int
    status: RunStatus
    passed: bool
    output_hash: str | None
    error_message: str | None = None


@dataclass
class BundleAnalysis:
    bundle_id: str
    label: StabilityLabel
    unique_output_hash_count: int
    pass_count: int
    fail_count: int
    timeout_count: int
    error_count: int
    ambiguous_count: int
    runs: list[RunRecord] = field(default_factory=list)


@dataclass
class OutputStabilityResult:
    artifact_id: str
    functionally_valid: bool
    validation_error: str | None
    bundle_results: list[BundleAnalysis]
    label: StabilityLabel

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for bundle in payload["bundle_results"]:
            bundle["runs"] = [asdict(r) for r in bundle["runs"]]
        return payload


class _Timeout(Exception):
    pass


def _timeout_handler(signum: int, frame: Any) -> None:
    raise _Timeout()


def detector_source_path() -> Path:
    return Path(__file__).resolve()


def project_root() -> Path:
    return detector_source_path().parents[2]


def detector_sha256() -> str:
    return hashlib.sha256(detector_source_path().read_bytes()).hexdigest()


def write_sha256_file(path: Path | None = None) -> Path:
    root = project_root()
    out = path or (root / "external_variability_detector_sha256.txt")
    out.write_text(detector_sha256() + "\n", encoding="utf-8")
    return out


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root(),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def write_freeze_record(output_path: Path | None = None) -> Path:
    root = project_root()
    out = output_path or (root / "results" / "external_variability" / "output_stability_freeze.json")
    payload = {
        "detector_module": "invert_external.detectors.output_stability",
        "detector_path": "invert_external/detectors/output_stability.py",
        "sha256": detector_sha256(),
        "git_commit": _git_commit(),
        "uses_invert_api": False,
        "separate_from_class_e": True,
        "class_e_detector_path": "src/invert_core/detectors/deterministic_randomized.py",
        "note": "Frozen before external output-stability pilot",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def normalize_output(
    value: Any,
    *,
    sort_collections: bool = False,
    normalize_whitespace: bool = True,
    max_output_chars: int = 65536,
) -> str | None:
    def _normalize(value: Any) -> str | None:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return None
            return repr(value)
        if isinstance(value, str):
            text = " ".join(value.split()) if normalize_whitespace else value
            return json.dumps(text, ensure_ascii=False)
        if isinstance(value, bytes):
            try:
                text = value.decode("utf-8")
            except UnicodeDecodeError:
                return None
            if normalize_whitespace:
                text = " ".join(text.split())
            return json.dumps(text, ensure_ascii=False)
        if isinstance(value, tuple):
            parts = [_normalize(item) for item in value]
            if any(part is None for part in parts):
                return None
            return "(" + ",".join(parts) + ")"
        if isinstance(value, list):
            parts = [_normalize(item) for item in value]
            if any(part is None for part in parts):
                return None
            return "[" + ",".join(parts) + "]"
        if isinstance(value, set):
            if not sort_collections:
                return None
            parts = sorted(
                normalized
                for item in value
                if (normalized := _normalize(item)) is not None
            )
            if len(parts) != len(value):
                return None
            return "{" + ",".join(parts) + "}"
        if isinstance(value, dict):
            items: list[tuple[str, str]] = []
            for key, item in value.items():
                key_norm = _normalize(key)
                val_norm = _normalize(item)
                if key_norm is None or val_norm is None:
                    return None
                items.append((key_norm, val_norm))
            if sort_collections:
                items.sort(key=lambda pair: pair[0])
            return "{" + ",".join(f"{k}:{v}" for k, v in items) + "}"
        if isinstance(value, (complex, type(Ellipsis))):
            return None
        try:
            encoded = json.dumps(value, sort_keys=sort_collections, ensure_ascii=False)
        except (TypeError, ValueError):
            return None
        if encoded == "null" and value is not None:
            return None
        return encoded

    normalized = _normalize(value)
    if normalized is None or len(normalized) > max_output_chars:
        return None
    return normalized


def hash_normalized_output(normalized: str) -> str:
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _fresh_namespace(code: str) -> dict[str, Any]:
    namespace: dict[str, Any] = {"__builtins__": __builtins__}
    exec(code, namespace, namespace)
    return namespace


class _alarm_context:
    def __init__(self, timeout_sec: float) -> None:
        self._timeout_sec = timeout_sec
        self._previous: Any = None

    def __enter__(self) -> None:
        self._previous = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, self._timeout_sec)

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, self._previous)
        return False


def _execute_in_namespace(
    namespace: dict[str, Any],
    entry_point: str,
    args: tuple[Any, ...],
    *,
    protocol: OutputStabilityProtocol,
    sort_collections: bool,
) -> tuple[RunRecord, Any | None]:
    candidate = namespace.get(entry_point)
    if not callable(candidate):
        return (
            RunRecord(-1, "error", False, None, f"entry_point_not_callable:{entry_point}"),
            None,
        )
    try:
        with _alarm_context(protocol.timeout_sec):
            result = candidate(*args)
    except _Timeout:
        return RunRecord(-1, "timeout", False, None, "timeout"), None
    except Exception as exc:
        return (
            RunRecord(-1, "error", False, None, f"{type(exc).__name__}: {exc}"),
            None,
        )

    normalized = normalize_output(
        result,
        sort_collections=sort_collections,
        normalize_whitespace=protocol.normalize_whitespace,
        max_output_chars=protocol.max_output_chars,
    )
    if normalized is None:
        return (
            RunRecord(-1, "ambiguous", False, None, "output_normalization_failed"),
            result,
        )
    return (
        RunRecord(-1, "pass", True, hash_normalized_output(normalized), None),
        result,
    )


def classify_run_records(
    records: Sequence[RunRecord],
    *,
    validator_passed: Sequence[bool] | None = None,
) -> StabilityLabel:
    if not records:
        return "error"
    if any(record.status == "timeout" for record in records):
        return "timeout"
    if any(record.status == "ambiguous" for record in records):
        return "ambiguous"

    passed_flags = list(validator_passed) if validator_passed is not None else [
        record.passed for record in records
    ]
    error_count = sum(1 for record in records if record.status == "error")
    if error_count == len(records):
        return "error"

    pass_count = sum(1 for flag in passed_flags if flag)
    fail_count = len(records) - pass_count
    if pass_count > 0 and fail_count > 0:
        return "flaky_invalid"
    if pass_count == 0:
        return "error"

    hashes = {
        record.output_hash
        for record, flag in zip(records, passed_flags)
        if flag and record.output_hash is not None
    }
    if not hashes:
        return "ambiguous"
    if len(hashes) == 1:
        return "stable"
    return "variable"


def analyze_bundle(
    code: str,
    *,
    entry_point: str,
    bundle: InputBundle,
    protocol: OutputStabilityProtocol,
    validator: Callable[[Any], bool],
) -> BundleAnalysis:
    namespace = _fresh_namespace(code)
    execution_records: list[RunRecord] = []
    validator_flags: list[bool] = []

    for run_index in range(protocol.run_count):
        record, output = _execute_in_namespace(
            namespace,
            entry_point,
            bundle.args,
            protocol=protocol,
            sort_collections=bundle.sort_output_for_comparison,
        )
        if record.status == "pass" and output is not None:
            validator_flags.append(bool(validator(output)))
        else:
            validator_flags.append(False)
        execution_records.append(
            RunRecord(
                run_index=run_index,
                status=record.status,
                passed=record.passed,
                output_hash=record.output_hash,
                error_message=record.error_message,
            )
        )

    label = classify_run_records(execution_records, validator_passed=validator_flags)
    unique_hashes = {
        record.output_hash
        for record, flag in zip(execution_records, validator_flags)
        if flag and record.output_hash is not None
    }
    return BundleAnalysis(
        bundle_id=bundle.bundle_id,
        label=label,
        unique_output_hash_count=len(unique_hashes),
        pass_count=sum(1 for flag in validator_flags if flag),
        fail_count=sum(1 for flag in validator_flags if not flag),
        timeout_count=sum(1 for r in execution_records if r.status == "timeout"),
        error_count=sum(1 for r in execution_records if r.status == "error"),
        ambiguous_count=sum(1 for r in execution_records if r.status == "ambiguous"),
        runs=execution_records,
    )


def _aggregate_labels(labels: Sequence[StabilityLabel]) -> StabilityLabel:
    if not labels:
        return "error"
    for label in ("timeout", "error", "ambiguous", "flaky_invalid", "variable", "stable"):
        if label in labels:
            return label  # type: ignore[return-value]
    return labels[0]


def analyze_output_stability(
    code: str,
    *,
    artifact_id: str,
    entry_point: str,
    bundles: Sequence[InputBundle],
    protocol: OutputStabilityProtocol,
    validators: dict[str, Callable[[Any], bool]],
    functionally_valid: bool,
    validation_error: str | None = None,
) -> OutputStabilityResult:
    """Analyze output stability after external functional validation."""

    if not functionally_valid:
        return OutputStabilityResult(
            artifact_id=artifact_id,
            functionally_valid=False,
            validation_error=validation_error,
            bundle_results=[],
            label="invalid",
        )

    bundle_results = [
        analyze_bundle(
            code,
            entry_point=entry_point,
            bundle=bundle,
            protocol=protocol,
            validator=validators[bundle.bundle_id],
        )
        for bundle in bundles
    ]
    return OutputStabilityResult(
        artifact_id=artifact_id,
        functionally_valid=True,
        validation_error=None,
        bundle_results=bundle_results,
        label=_aggregate_labels([b.label for b in bundle_results]),
    )
