from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from invert_core.deterministic_randomized_tasks import (
    DeterministicRandomizedTask,
    load_deterministic_randomized_tasks,
)
from invert_core.tasks import project_root

DetectionMode = Literal["primary", "fixed_seed_control"]
DEFAULT_RUN_COUNT = 5
DEFAULT_FIXED_SEED = 12345


@dataclass
class DeterministicRandomizedResult:
    method: str
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"method": self.method, "evidence": self.evidence}


def is_genuine_deterministic(evidence: dict[str, Any]) -> bool:
    return int(evidence.get("unique_trace_count", 0)) == 1


def is_genuine_randomized(evidence: dict[str, Any]) -> bool:
    return int(evidence.get("unique_trace_count", 0)) >= 2


def pole_manipulation_success(requested_method: str, evidence: dict[str, Any]) -> bool:
    if requested_method == "deterministic":
        return is_genuine_deterministic(evidence)
    if requested_method == "randomized":
        return is_genuine_randomized(evidence)
    return False


def _load_item_processor(code: str) -> tuple[type | None, str | None]:
    namespace: dict[str, Any] = {"__builtins__": __builtins__}
    try:
        exec(code, namespace, namespace)
    except Exception as exc:
        return None, f"exec_failed: {exc}"
    cls = namespace.get("ItemProcessor")
    if not isinstance(cls, type):
        return None, "no_item_processor_class"
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


def _collect_traces(
    cls: type,
    task: DeterministicRandomizedTask,
    *,
    seed: int | None,
    run_count: int,
) -> tuple[list[list[Any]], bool, str | None]:
    traces: list[list[Any]] = []
    expected = set(task.expected_items)
    all_outputs_valid = True

    for _ in range(run_count):
        trace: list[Any] = []

        def visit_fn(item: Any) -> None:
            trace.append(item)

        try:
            processor = cls(task.items, visit_fn, seed=seed)
            output = processor.process_all()
        except Exception as exc:
            return traces, False, f"execution_failed: {exc}"

        got = _normalize_output(output)
        if got != expected:
            all_outputs_valid = False
        traces.append(list(trace))

    return traces, all_outputs_valid, None


def _classify_traces(
    traces: list[list[Any]],
    *,
    all_outputs_valid: bool,
    run_count: int,
    expected_items: list[Any],
    mode: DetectionMode,
    seed: int | None,
) -> DeterministicRandomizedResult:
    unique_traces = {tuple(t) for t in traces}
    unique_trace_count = len(unique_traces)

    evidence: dict[str, Any] = {
        "traces": traces,
        "unique_trace_count": unique_trace_count,
        "run_count": run_count,
        "expected_items": expected_items,
        "all_outputs_valid": all_outputs_valid,
        "mode": mode,
        "seed": seed,
    }

    if not traces or not all_outputs_valid:
        evidence["reason"] = "invalid_outputs_or_failed_runs"
        return DeterministicRandomizedResult(method="ambiguous", evidence=evidence)

    if unique_trace_count == 1:
        evidence["reason"] = "identical_traces_across_runs"
        return DeterministicRandomizedResult(method="deterministic", evidence=evidence)

    if unique_trace_count >= 2:
        evidence["reason"] = "variable_traces_across_runs"
        return DeterministicRandomizedResult(method="randomized", evidence=evidence)

    evidence["reason"] = "insufficient_trace_evidence"
    return DeterministicRandomizedResult(method="ambiguous", evidence=evidence)


def detect_deterministic_randomized(
    code: str,
    task: DeterministicRandomizedTask,
    *,
    mode: DetectionMode = "primary",
    run_count: int = DEFAULT_RUN_COUNT,
    fixed_seed: int = DEFAULT_FIXED_SEED,
) -> DeterministicRandomizedResult:
    cls, err = _load_item_processor(code)
    if cls is None:
        return DeterministicRandomizedResult(
            method="ambiguous",
            evidence={
                "traces": [],
                "unique_trace_count": 0,
                "run_count": run_count,
                "expected_items": task.expected_items,
                "all_outputs_valid": False,
                "mode": mode,
                "seed": None if mode == "primary" else fixed_seed,
                "reason": err or "load_failed",
            },
        )

    seed = None if mode == "primary" else fixed_seed
    traces, all_outputs_valid, run_err = _collect_traces(
        cls, task, seed=seed, run_count=run_count
    )
    if run_err:
        return DeterministicRandomizedResult(
            method="ambiguous",
            evidence={
                "traces": traces,
                "unique_trace_count": len({tuple(t) for t in traces}),
                "run_count": run_count,
                "expected_items": task.expected_items,
                "all_outputs_valid": False,
                "mode": mode,
                "seed": seed,
                "reason": run_err,
            },
        )

    return _classify_traces(
        traces,
        all_outputs_valid=all_outputs_valid,
        run_count=run_count,
        expected_items=task.expected_items,
        mode=mode,
        seed=seed,
    )


def detect_deterministic_randomized_file(
    path: str,
    *,
    task_id: str,
    mode: DetectionMode = "primary",
    run_count: int = DEFAULT_RUN_COUNT,
    fixed_seed: int = DEFAULT_FIXED_SEED,
) -> DeterministicRandomizedResult:
    tasks_file = (
        project_root()
        / "data"
        / "core_v2"
        / "tasks"
        / "deterministic_randomized_tasks.json"
    )
    tasks_by_id = {t.task_id: t for t in load_deterministic_randomized_tasks(tasks_file)}
    if task_id not in tasks_by_id:
        raise ValueError(f"Unknown task_id: {task_id}")
    code = open(path, encoding="utf-8").read()
    return detect_deterministic_randomized(
        code,
        tasks_by_id[task_id],
        mode=mode,
        run_count=run_count,
        fixed_seed=fixed_seed,
    )
