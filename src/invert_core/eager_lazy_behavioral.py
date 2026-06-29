from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from invert_core.detectors.eager_lazy import CallbackInstrumentation, _load_pipeline_class
from invert_core.eager_lazy_tasks import EagerLazyTask, default_feature_fns


@dataclass
class EagerLazyBehavioralResult:
    parsed: bool
    behavioral_pass: bool
    error: str | None = None

    @property
    def manipulation_success(self) -> bool:
        return self.parsed and self.behavioral_pass


def _expected_values(task: EagerLazyTask) -> dict[str, int]:
    return {
        "feature_a": task.expected_feature_a,
        "feature_b": task.expected_feature_b,
        "feature_c": task.expected_feature_c,
    }


def run_eager_lazy_behavioral_oracle(
    code: str, task: EagerLazyTask
) -> EagerLazyBehavioralResult:
    cls, getters, err = _load_pipeline_class(code)
    if cls is None:
        return EagerLazyBehavioralResult(parsed=False, behavioral_pass=False, error=err)

    required_getters = ["get_feature_a", "get_feature_b", "get_feature_c"]
    if not all(name in getters for name in required_getters):
        return EagerLazyBehavioralResult(
            parsed=False, behavioral_pass=False, error="missing_required_getters"
        )

    tracker = CallbackInstrumentation()
    base_a, base_b, base_c = default_feature_fns()
    fns = (
        tracker.wrap("feature_a", base_a),
        tracker.wrap("feature_b", base_b),
        tracker.wrap("feature_c", base_c),
    )

    try:
        pipeline = cls(task.x, *fns)
    except TypeError:
        return EagerLazyBehavioralResult(
            parsed=False, behavioral_pass=False, error="constructor_signature_mismatch"
        )
    except Exception as exc:
        return EagerLazyBehavioralResult(
            parsed=True, behavioral_pass=False, error=f"instantiation_failed: {exc}"
        )

    expected = _expected_values(task)
    try:
        for getter, key in [
            ("get_feature_a", "feature_a"),
            ("get_feature_b", "feature_b"),
            ("get_feature_c", "feature_c"),
        ]:
            first = getattr(pipeline, getter)()
            if first != expected[key]:
                return EagerLazyBehavioralResult(
                    parsed=True,
                    behavioral_pass=False,
                    error=f"wrong_value_{key}",
                )
            second = getattr(pipeline, getter)()
            if second != first:
                return EagerLazyBehavioralResult(
                    parsed=True,
                    behavioral_pass=False,
                    error=f"inconsistent_repeat_{key}",
                )
    except Exception as exc:
        return EagerLazyBehavioralResult(
            parsed=True, behavioral_pass=False, error=f"runtime_error: {exc}"
        )

    return EagerLazyBehavioralResult(parsed=True, behavioral_pass=True)
