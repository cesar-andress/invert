from __future__ import annotations

from dataclasses import dataclass

from invert_core.detectors.bfs_dfs import _load_traversal_class
from invert_core.bfs_dfs_tasks import BfsDfsTask


@dataclass
class BfsDfsBehavioralResult:
    parsed: bool
    behavioral_pass: bool
    error: str | None = None

    @property
    def manipulation_success(self) -> bool:
        return self.parsed and self.behavioral_pass


def run_bfs_dfs_behavioral_oracle(code: str, task: BfsDfsTask) -> BfsDfsBehavioralResult:
    cls, reachable_method, err = _load_traversal_class(code)
    if cls is None or reachable_method is None:
        return BfsDfsBehavioralResult(parsed=False, behavioral_pass=False, error=err)

    if cls.__name__ != "GraphTraversal":
        return BfsDfsBehavioralResult(
            parsed=False, behavioral_pass=False, error="wrong_class_name"
        )

    visit_trace: list[str] = []

    def visit_fn(node: str) -> None:
        visit_trace.append(node)

    try:
        traversal = cls(task.graph, task.start, visit_fn)
    except TypeError:
        return BfsDfsBehavioralResult(
            parsed=False, behavioral_pass=False, error="constructor_signature_mismatch"
        )
    except Exception as exc:
        return BfsDfsBehavioralResult(
            parsed=True, behavioral_pass=False, error=f"instantiation_failed: {exc}"
        )

    try:
        result = getattr(traversal, reachable_method)()
    except Exception as exc:
        return BfsDfsBehavioralResult(
            parsed=True, behavioral_pass=False, error=f"runtime_error: {exc}"
        )

    expected = set(task.expected_reachable)
    if isinstance(result, set):
        reachable = set(result)
    elif isinstance(result, list):
        reachable = set(result)
    else:
        try:
            reachable = set(result)
        except Exception:
            return BfsDfsBehavioralResult(
                parsed=True, behavioral_pass=False, error="invalid_return_type"
            )

    if reachable != expected:
        return BfsDfsBehavioralResult(
            parsed=True, behavioral_pass=False, error="wrong_reachable_set"
        )

    if len(visit_trace) != len(set(visit_trace)):
        return BfsDfsBehavioralResult(
            parsed=True, behavioral_pass=False, error="duplicate_visits"
        )

    if set(visit_trace) != expected:
        return BfsDfsBehavioralResult(
            parsed=True, behavioral_pass=False, error="visited_unreachable_or_missing"
        )

    return BfsDfsBehavioralResult(parsed=True, behavioral_pass=True)
