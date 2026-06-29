from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from invert_core.eager_lazy_tasks import EagerLazyTask, default_feature_fns

DemandPattern = Literal["partial", "full"]

FEATURE_KEYS = ("feature_a", "feature_b", "feature_c")
CALLBACK_ATTRS = ("feature_a_fn", "feature_b_fn", "feature_c_fn")


@dataclass
class CallbackInstrumentation:
    trace: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=lambda: {k: 0 for k in FEATURE_KEYS})

    def snapshot_counts(self) -> dict[str, int]:
        return dict(self.counts)

    def wrap(self, name: str, impl: Callable[[list[int]], int]) -> Callable[[list[int]], int]:
        def wrapped(x: list[int]) -> int:
            self.trace.append(f"{name}:call")
            self.counts[name] += 1
            return impl(x)

        return wrapped

    def computed_features(self) -> list[str]:
        return [name for name in FEATURE_KEYS if self.counts[name] > 0]

    def total_calls(self) -> int:
        return sum(self.counts.values())


@dataclass
class EagerLazyResult:
    method: str
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"method": self.method, "evidence": self.evidence}


def is_genuine_eager(evidence: dict[str, Any]) -> bool:
    """All features computed before the first explicit getter request."""
    return (
        set(evidence.get("computed_features_before_request", [])) == set(FEATURE_KEYS)
        and int(evidence.get("calls_before_first_request", 0)) >= 3
        and int(evidence.get("calls_during_first_request", 0)) == 0
    )


def is_genuine_lazy(evidence: dict[str, Any]) -> bool:
    """No feature computed before request; first getter computes only feature_a."""
    return (
        int(evidence.get("calls_before_first_request", 0)) == 0
        and not bool(evidence.get("unrequested_features_computed"))
        and int(evidence.get("calls_during_first_request", 0)) == 1
        and set(evidence.get("computed_features_before_request", [])) == set()
        and set(evidence.get("computed_features_on_demand", [])) == {"feature_a"}
    )


def pole_manipulation_success(requested_method: str, evidence: dict[str, Any]) -> bool:
    if requested_method == "eager":
        return is_genuine_eager(evidence)
    if requested_method == "lazy":
        return is_genuine_lazy(evidence)
    return False


def _ambiguous(reason: str, **extra: Any) -> EagerLazyResult:
    evidence: dict[str, Any] = {
        "calls_before_first_request": extra.get("calls_before_first_request", 0),
        "calls_during_first_request": extra.get("calls_during_first_request", 0),
        "calls_during_second_request": extra.get("calls_during_second_request", 0),
        "calls_during_third_request": extra.get("calls_during_third_request", 0),
        "calls_after_unrequested_feature": extra.get("calls_after_unrequested_feature", 0),
        "computed_features_before_request": extra.get("computed_features_before_request", []),
        "computed_features_on_demand": extra.get("computed_features_on_demand", []),
        "unrequested_features_computed": extra.get("unrequested_features_computed", False),
        "trace": extra.get("trace", []),
        "demand_pattern": extra.get("demand_pattern", "partial"),
        "reason": reason,
    }
    return EagerLazyResult(method="ambiguous", evidence=evidence)


def _find_pipeline_class(code: str) -> tuple[str | None, list[str], str | None]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None, [], "syntax_error"

    candidates: list[tuple[str, list[str]]] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        init_args = 0
        getters: list[str] = []
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            if item.name == "__init__":
                init_args = len(item.args.args)
            elif item.name.startswith("__") and item.name.endswith("__"):
                continue
            elif len(item.args.args) == 1:
                getters.append(item.name)
        if init_args >= 4 and len(getters) >= 3:
            candidates.append((node.name, getters[:3]))

    for name, getters in candidates:
        if name == "FeaturePipeline":
            return name, getters, None
    if candidates:
        name, getters = candidates[0]
        return name, getters, None
    return None, [], "no_pipeline_class"


def _resolve_getter(getters: list[str], feature: str) -> str | None:
    preferred = f"get_feature_{feature[-1]}"
    if preferred in getters:
        return preferred
    order = {"a": 0, "b": 1, "c": 2}
    idx = order.get(feature[-1], 0)
    if idx < len(getters):
        return getters[idx]
    return getters[0] if getters else None


def _load_pipeline_class(code: str) -> tuple[type | None, list[str], str | None]:
    class_name, getters, err = _find_pipeline_class(code)
    if class_name is None:
        return None, [], err
    namespace: dict[str, Any] = {"__builtins__": __builtins__}
    try:
        exec(code, namespace, namespace)
    except Exception as exc:
        return None, [], f"exec_failed: {exc}"
    cls = namespace.get(class_name)
    if not isinstance(cls, type):
        return None, [], "pipeline_class_not_found"
    return cls, getters, None


def _delta_counts(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    return {k: after.get(k, 0) - before.get(k, 0) for k in FEATURE_KEYS}


def _classify_partial_demand(evidence: dict[str, Any], calls_after_repeat: int) -> EagerLazyResult:
    if calls_after_repeat > 0:
        evidence["reason"] = "recompute_on_repeat_getter"
        return EagerLazyResult(method="ambiguous", evidence=evidence)

    calls_before = int(evidence["calls_before_first_request"])
    calls_during = int(evidence["calls_during_first_request"])
    computed_before = evidence["computed_features_before_request"]
    computed_after_first = set(computed_before) | set(evidence["computed_features_on_demand"])
    unrequested_computed = bool(evidence["unrequested_features_computed"])

    all_features = set(FEATURE_KEYS)
    if set(computed_before) == all_features and calls_during == 0:
        evidence["reason"] = "all_features_precomputed_before_first_request"
        return EagerLazyResult(method="eager", evidence=evidence)

    if (
        calls_before == 0
        and calls_during == 1
        and computed_after_first == {"feature_a"}
        and not unrequested_computed
    ):
        evidence["reason"] = "single_feature_on_demand_with_cache"
        return EagerLazyResult(method="lazy", evidence=evidence)

    if len(computed_after_first) == 0 and calls_before == 0:
        evidence["reason"] = "no_feature_computation_observed"
        return EagerLazyResult(method="ambiguous", evidence=evidence)

    evidence["reason"] = "timing_trace_does_not_distinguish_eager_lazy"
    return EagerLazyResult(method="ambiguous", evidence=evidence)


def _classify_full_demand_control(evidence: dict[str, Any], calls_after_repeat: int) -> EagerLazyResult:
    """Classify after all getters were requested; lazy pole should collapse to ambiguous."""
    if calls_after_repeat > 0:
        evidence["reason"] = "recompute_on_repeat_getter"
        return EagerLazyResult(method="ambiguous", evidence=evidence)

    all_features = set(FEATURE_KEYS)
    computed_before = set(evidence["computed_features_before_request"])
    calls_before = int(evidence["calls_before_first_request"])

    if computed_before == all_features and calls_before >= 3:
        evidence["reason"] = "all_features_precomputed_before_first_request"
        return EagerLazyResult(method="eager", evidence=evidence)

    evidence["reason"] = "full_demand_no_avoidable_computation_remaining"
    return EagerLazyResult(method="ambiguous", evidence=evidence)


def detect_eager_lazy(
    code: str,
    *,
    task: EagerLazyTask | None = None,
    x: list[int] | None = None,
    demand_pattern: DemandPattern = "partial",
) -> EagerLazyResult:
    cls, getters, err = _load_pipeline_class(code)
    if cls is None:
        return _ambiguous(err or "load_failed", demand_pattern=demand_pattern)

    getter_a = _resolve_getter(getters, "feature_a")
    getter_b = _resolve_getter(getters, "feature_b")
    getter_c = _resolve_getter(getters, "feature_c")
    if getter_a is None or getter_b is None or getter_c is None:
        return _ambiguous("missing_getter", demand_pattern=demand_pattern)

    input_x = x if x is not None else (task.x if task is not None else [1, 2, 3, 4])
    base_a, base_b, base_c = default_feature_fns()
    tracker = CallbackInstrumentation()
    fns = (
        tracker.wrap("feature_a", base_a),
        tracker.wrap("feature_b", base_b),
        tracker.wrap("feature_c", base_c),
    )

    try:
        pipeline = cls(input_x, *fns)
    except Exception as exc:
        return _ambiguous(
            f"instantiation_failed: {exc}",
            trace=list(tracker.trace),
            demand_pattern=demand_pattern,
        )

    before_counts = tracker.snapshot_counts()
    calls_before = tracker.total_calls()
    computed_before = tracker.computed_features()

    counts_pre_first = tracker.snapshot_counts()
    try:
        getattr(pipeline, getter_a)()
    except Exception as exc:
        return _ambiguous(
            f"first_getter_failed: {exc}",
            calls_before_first_request=calls_before,
            computed_features_before_request=computed_before,
            trace=list(tracker.trace),
            demand_pattern=demand_pattern,
        )

    after_first_counts = tracker.snapshot_counts()
    during_first = _delta_counts(counts_pre_first, after_first_counts)
    calls_during = sum(during_first.values())
    computed_after_first = tracker.computed_features()

    calls_during_second = 0
    calls_during_third = 0
    if demand_pattern == "full":
        counts_pre_second = tracker.snapshot_counts()
        try:
            getattr(pipeline, getter_b)()
        except Exception as exc:
            return _ambiguous(
                f"second_getter_failed: {exc}",
                calls_before_first_request=calls_before,
                calls_during_first_request=calls_during,
                computed_features_before_request=computed_before,
                trace=list(tracker.trace),
                demand_pattern=demand_pattern,
            )
        calls_during_second = sum(_delta_counts(counts_pre_second, tracker.snapshot_counts()).values())

        counts_pre_third = tracker.snapshot_counts()
        try:
            getattr(pipeline, getter_c)()
        except Exception as exc:
            return _ambiguous(
                f"third_getter_failed: {exc}",
                calls_before_first_request=calls_before,
                calls_during_first_request=calls_during,
                calls_during_second_request=calls_during_second,
                computed_features_before_request=computed_before,
                trace=list(tracker.trace),
                demand_pattern=demand_pattern,
            )
        calls_during_third = sum(_delta_counts(counts_pre_third, tracker.snapshot_counts()).values())

    counts_pre_repeat = tracker.snapshot_counts()
    getattr(pipeline, getter_a)()
    calls_after_repeat = sum(_delta_counts(counts_pre_repeat, tracker.snapshot_counts()).values())

    unrequested = {"feature_b", "feature_c"}
    unrequested_computed = any(name in computed_after_first for name in unrequested) or any(
        before_counts[name] > 0 for name in unrequested
    )

    on_demand = [name for name in computed_after_first if before_counts.get(name, 0) == 0]

    evidence: dict[str, Any] = {
        "calls_before_first_request": calls_before,
        "calls_during_first_request": calls_during,
        "calls_during_second_request": calls_during_second,
        "calls_during_third_request": calls_during_third,
        "calls_after_unrequested_feature": sum(
            before_counts.get(name, 0) for name in unrequested
        ),
        "computed_features_before_request": computed_before,
        "computed_features_on_demand": on_demand,
        "unrequested_features_computed": unrequested_computed,
        "trace": list(tracker.trace),
        "demand_pattern": demand_pattern,
    }

    if demand_pattern == "full":
        return _classify_full_demand_control(evidence, calls_after_repeat)
    return _classify_partial_demand(evidence, calls_after_repeat)


def detect_eager_lazy_file(
    path: str,
    *,
    task: EagerLazyTask | None = None,
    x: list[int] | None = None,
    demand_pattern: DemandPattern = "partial",
) -> EagerLazyResult:
    code = open(path, encoding="utf-8").read()
    return detect_eager_lazy(code, task=task, x=x, demand_pattern=demand_pattern)
