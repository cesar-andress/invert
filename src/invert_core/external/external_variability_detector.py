from __future__ import annotations

import hashlib
import json
import math
import signal
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, Sequence

VariabilityLabel = Literal[
    "stable",
    "variable",
    "flaky_invalid",
    "timeout",
    "error",
    "ambiguous",
]

RunStatus = Literal["pass", "fail", "timeout", "error", "ambiguous"]


@dataclass(frozen=True)
class InputBundle:
    """Fixed inputs for one repeated-execution bundle."""

    bundle_id: str
    args: tuple[Any, ...] = ()
    sort_output_for_comparison: bool = False


@dataclass(frozen=True)
class ExternalVariabilityProtocol:
    """Frozen protocol parameters (see configs/external_variability_protocol.yaml)."""

    run_count: int = 10
    timeout_sec: float = 2.0
    python_hashseed: str = "0"
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
    label: VariabilityLabel
    unique_output_hash_count: int
    pass_count: int
    fail_count: int
    timeout_count: int
    error_count: int
    ambiguous_count: int
    runs: list[RunRecord] = field(default_factory=list)


@dataclass
class ExternalVariabilityResult:
    artifact_id: str
    externally_valid: bool
    validation_passed: bool
    validation_error: str | None
    bundle_results: list[BundleAnalysis]
    aggregate_label: VariabilityLabel

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
    return detector_source_path().parents[3]


def detector_sha256() -> str:
    return hashlib.sha256(detector_source_path().read_bytes()).hexdigest()


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
    """Record detector SHA256 and git commit before external evaluation."""
    root = project_root()
    out = output_path or (
        root / "results" / "external_variability" / "detector_freeze.json"
    )
    payload = {
        "detector_module": "invert_core.external.external_variability_detector",
        "detector_path": str(detector_source_path().relative_to(root)),
        "sha256": detector_sha256(),
        "git_commit": _git_commit(),
        "uses_invert_api": False,
        "separate_from_class_e": True,
        "class_e_detector_path": "src/invert_core/detectors/deterministic_randomized.py",
        "note": "Frozen before external variability study scoring",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def load_protocol(path: Path | str) -> ExternalVariabilityProtocol:
    import yaml

    with open(path, encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    protocol = raw.get("protocol", raw)
    return ExternalVariabilityProtocol(
        run_count=int(protocol["run_count"]),
        timeout_sec=float(protocol["timeout_sec"]),
        python_hashseed=str(protocol.get("python_hashseed", "0")),
        normalize_whitespace=bool(protocol.get("normalize_whitespace", True)),
        max_output_chars=int(protocol.get("max_output_chars", 65536)),
    )


def normalize_output(
    value: Any,
    *,
    sort_collections: bool = False,
    normalize_whitespace: bool = True,
    max_output_chars: int = 65536,
) -> str | None:
    """Serialize output for hashing. Returns None when normalization is unsafe."""

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
            text = value
            if normalize_whitespace:
                text = " ".join(text.split())
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
    if normalized is None:
        return None
    if len(normalized) > max_output_chars:
        return None
    return normalized


def hash_normalized_output(normalized: str) -> str:
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _fresh_namespace(code: str) -> dict[str, Any]:
    namespace: dict[str, Any] = {"__builtins__": __builtins__}
    exec(code, namespace, namespace)
    return namespace


def _execute_in_namespace(
    namespace: dict[str, Any],
    entry_point: str,
    args: tuple[Any, ...],
    *,
    protocol: ExternalVariabilityProtocol,
    sort_collections: bool,
) -> tuple[RunRecord, Any | None]:
    candidate = namespace.get(entry_point)
    if not callable(candidate):
        return (
            RunRecord(
                run_index=-1,
                status="error",
                passed=False,
                output_hash=None,
                error_message=f"entry_point_not_callable:{entry_point}",
            ),
            None,
        )

    try:
        with _alarm_context(protocol.timeout_sec):
            result = candidate(*args)
    except _Timeout:
        return (
            RunRecord(
                run_index=-1,
                status="timeout",
                passed=False,
                output_hash=None,
                error_message="timeout",
            ),
            None,
        )
    except Exception as exc:
        return (
            RunRecord(
                run_index=-1,
                status="error",
                passed=False,
                output_hash=None,
                error_message=f"{type(exc).__name__}: {exc}",
            ),
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
            RunRecord(
                run_index=-1,
                status="ambiguous",
                passed=False,
                output_hash=None,
                error_message="output_normalization_failed",
            ),
            result,
        )
    return (
        RunRecord(
            run_index=-1,
            status="pass",
            passed=True,
            output_hash=hash_normalized_output(normalized),
            error_message=None,
        ),
        result,
    )


def classify_run_records(
    records: Sequence[RunRecord],
    *,
    validator_passed: Sequence[bool] | None = None,
) -> VariabilityLabel:
    """Apply frozen classification rules to N repeated runs."""

    if not records:
        return "error"

    if any(record.status == "timeout" for record in records):
        return "timeout"

    if validator_passed is not None:
        passed_flags = list(validator_passed)
    else:
        passed_flags = [record.passed for record in records]

    if any(record.status == "ambiguous" for record in records):
        return "ambiguous"

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
    protocol: ExternalVariabilityProtocol,
    validator: Callable[[Any], bool],
) -> BundleAnalysis:
    """Run N executions for one input bundle and classify variability."""

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
        timeout_count=sum(1 for record in execution_records if record.status == "timeout"),
        error_count=sum(1 for record in execution_records if record.status == "error"),
        ambiguous_count=sum(
            1 for record in execution_records if record.status == "ambiguous"
        ),
        runs=execution_records,
    )


class _alarm_context:
    def __init__(self, timeout_sec: float) -> None:
        self._timeout_sec = timeout_sec
        self._previous: Any = None

    def __enter__(self) -> None:
        self._previous = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, self._timeout_sec)

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, self._previous)
        if exc_type is _Timeout:
            return False
        return False


def run_behavioral_validation(
    code: str,
    *,
    entry_point: str,
    bundle: InputBundle,
    protocol: ExternalVariabilityProtocol,
    validator: Callable[[Any], bool],
) -> tuple[bool, str | None]:
    """First-pass functional validation before variability scoring."""

    try:
        namespace = _fresh_namespace(code)
        record, output = _execute_in_namespace(
            namespace,
            entry_point,
            bundle.args,
            protocol=protocol,
            sort_collections=bundle.sort_output_for_comparison,
        )
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"

    if record.status == "timeout":
        return False, "timeout"
    if record.status == "error":
        return False, record.error_message or "error"
    if record.status == "ambiguous" or output is None:
        return False, "output_normalization_failed"

    if not validator(output):
        return False, "validation_failed"
    return True, None


def analyze_external_variability(
    code: str,
    *,
    artifact_id: str,
    entry_point: str,
    bundles: Sequence[InputBundle],
    protocol: ExternalVariabilityProtocol,
    validators: dict[str, Callable[[Any], bool]],
) -> ExternalVariabilityResult:
    """Analyze repeated-execution variability for one artifact across bundles."""

    bundle_results: list[BundleAnalysis] = []
    validation_passed = True
    validation_error: str | None = None

    for bundle in bundles:
        validator = validators[bundle.bundle_id]
        passed, error = run_behavioral_validation(
            code,
            entry_point=entry_point,
            bundle=bundle,
            protocol=protocol,
            validator=validator,
        )
        if not passed:
            validation_passed = False
            validation_error = error
            break

    if validation_passed:
        for bundle in bundles:
            validator = validators[bundle.bundle_id]
            bundle_results.append(
                analyze_bundle(
                    code,
                    entry_point=entry_point,
                    bundle=bundle,
                    protocol=protocol,
                    validator=validator,
                )
            )
        aggregate_label = _aggregate_labels([bundle.label for bundle in bundle_results])
    else:
        bundle_results = []
        aggregate_label = "error"

    return ExternalVariabilityResult(
        artifact_id=artifact_id,
        externally_valid=validation_passed,
        validation_passed=validation_passed,
        validation_error=validation_error,
        bundle_results=bundle_results,
        aggregate_label=aggregate_label,
    )


def _aggregate_labels(labels: Sequence[VariabilityLabel]) -> VariabilityLabel:
    if not labels:
        return "error"
    priority: list[VariabilityLabel] = [
        "timeout",
        "error",
        "ambiguous",
        "flaky_invalid",
        "variable",
        "stable",
    ]
    for label in priority:
        if label in labels:
            return label
    return labels[0]
