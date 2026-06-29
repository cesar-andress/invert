from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from invert_core.deterministic_randomized_tasks import DeterministicRandomizedTask


@dataclass
class DeterministicRandomizedBehavioralResult:
    parsed: bool
    behavioral_pass: bool
    error: str | None = None

    @property
    def manipulation_success(self) -> bool:
        return self.parsed and self.behavioral_pass


def _load_item_processor(code: str) -> tuple[type | None, str | None]:
    namespace: dict[str, Any] = {"__builtins__": __builtins__}
    try:
        exec(code, namespace, namespace)
    except Exception as exc:
        return None, f"exec_failed: {exc}"
    cls = namespace.get("ItemProcessor")
    if not isinstance(cls, type):
        return None, "no_item_processor_class"
    if cls.__name__ != "ItemProcessor":
        return None, "wrong_class_name"
    return cls, None


def _normalize_output(value: Any) -> set[Any] | None:
    if isinstance(value, set):
        return set(value)
    if isinstance(value, list):
        return set(value)
    try:
        return set(value)
    except Exception:
        return None


def run_deterministic_randomized_behavioral_oracle(
    code: str,
    task: DeterministicRandomizedTask,
) -> DeterministicRandomizedBehavioralResult:
    cls, err = _load_item_processor(code)
    if cls is None:
        return DeterministicRandomizedBehavioralResult(
            parsed=False, behavioral_pass=False, error=err
        )

    call_counts: dict[Any, int] = {}

    def visit_fn(item: Any) -> None:
        call_counts[item] = call_counts.get(item, 0) + 1

    try:
        processor = cls(task.items, visit_fn, seed=None)
    except TypeError:
        return DeterministicRandomizedBehavioralResult(
            parsed=False, behavioral_pass=False, error="constructor_signature_mismatch"
        )
    except Exception as exc:
        return DeterministicRandomizedBehavioralResult(
            parsed=True, behavioral_pass=False, error=f"instantiation_failed: {exc}"
        )

    if not hasattr(processor, "process_all"):
        return DeterministicRandomizedBehavioralResult(
            parsed=True, behavioral_pass=False, error="missing_process_all"
        )

    try:
        output = processor.process_all()
    except Exception as exc:
        return DeterministicRandomizedBehavioralResult(
            parsed=True, behavioral_pass=False, error=f"runtime_error: {exc}"
        )

    expected = set(task.expected_items)
    got = _normalize_output(output)
    if got is None:
        return DeterministicRandomizedBehavioralResult(
            parsed=True, behavioral_pass=False, error="invalid_return_type"
        )
    if got != expected:
        return DeterministicRandomizedBehavioralResult(
            parsed=True, behavioral_pass=False, error="wrong_output_set"
        )

    for item in expected:
        if call_counts.get(item, 0) != 1:
            return DeterministicRandomizedBehavioralResult(
                parsed=True,
                behavioral_pass=False,
                error="visit_fn_not_called_exactly_once_per_item",
            )

    if set(call_counts) != expected:
        return DeterministicRandomizedBehavioralResult(
            parsed=True, behavioral_pass=False, error="extra_or_missing_visit_fn_calls"
        )

    return DeterministicRandomizedBehavioralResult(parsed=True, behavioral_pass=True)
