from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any, Callable

from invert_core.bfs_dfs_tasks import BfsDfsTask, bfs_dfs_distances, load_bfs_dfs_tasks
from invert_core.tasks import project_root


@dataclass
class BfsDfsResult:
    method: str
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"method": self.method, "evidence": self.evidence}


def is_genuine_bfs(evidence: dict[str, Any]) -> bool:
    return bool(evidence.get("bfs_order_match")) and not bool(evidence.get("dfs_order_match"))


def is_genuine_dfs(evidence: dict[str, Any]) -> bool:
    return bool(evidence.get("dfs_order_match")) and not bool(evidence.get("bfs_order_match"))


def pole_manipulation_success(requested_method: str, evidence: dict[str, Any]) -> bool:
    if requested_method == "bfs":
        return is_genuine_bfs(evidence)
    if requested_method == "dfs":
        return is_genuine_dfs(evidence)
    return False


def _ambiguous(reason: str, **extra: Any) -> BfsDfsResult:
    evidence: dict[str, Any] = {
        "visit_trace": extra.get("visit_trace", []),
        "expected_reachable": extra.get("expected_reachable", []),
        "bfs_order_match": extra.get("bfs_order_match", False),
        "dfs_order_match": extra.get("dfs_order_match", False),
        "distances_from_start": extra.get("distances_from_start", {}),
        "reason": reason,
    }
    if "expected_bfs_order" in extra:
        evidence["expected_bfs_order"] = extra["expected_bfs_order"]
    if "expected_dfs_order" in extra:
        evidence["expected_dfs_order"] = extra["expected_dfs_order"]
    return BfsDfsResult(method="ambiguous", evidence=evidence)


def _find_traversal_class(code: str) -> tuple[str | None, str | None, str | None]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None, None, "syntax_error"

    candidates: list[tuple[str, str]] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        init_args = 0
        entry_methods: list[str] = []
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            if item.name == "__init__":
                init_args = len(item.args.args)
            elif item.name.startswith("__") and item.name.endswith("__"):
                continue
            elif len(item.args.args) == 1:
                entry_methods.append(item.name)
        if init_args >= 4 and entry_methods:
            reachable = (
                "reachable_nodes"
                if "reachable_nodes" in entry_methods
                else entry_methods[0]
            )
            candidates.append((node.name, reachable))

    for name, reachable in candidates:
        if name == "GraphTraversal":
            return name, reachable, None
    if candidates:
        name, reachable = candidates[0]
        return name, reachable, None
    return None, None, "no_graph_traversal_class"


def _load_traversal_class(code: str) -> tuple[type | None, str | None, str | None]:
    class_name, reachable_method, err = _find_traversal_class(code)
    if class_name is None or reachable_method is None:
        return None, None, err
    namespace: dict[str, Any] = {"__builtins__": __builtins__}
    try:
        exec(code, namespace, namespace)
    except Exception as exc:
        return None, None, f"exec_failed: {exc}"
    cls = namespace.get(class_name)
    if not isinstance(cls, type):
        return None, None, "graph_traversal_class_not_found"
    return cls, reachable_method, None


def _classify_trace(
    visit_trace: list[str],
    task: BfsDfsTask,
) -> BfsDfsResult:
    expected_bfs = task.expected_bfs_order
    expected_dfs = task.expected_dfs_order
    bfs_match = visit_trace == expected_bfs
    dfs_match = visit_trace == expected_dfs
    distances = bfs_dfs_distances(task.graph, task.start)

    evidence: dict[str, Any] = {
        "visit_trace": visit_trace,
        "expected_reachable": task.expected_reachable,
        "expected_bfs_order": expected_bfs,
        "expected_dfs_order": expected_dfs,
        "bfs_order_match": bfs_match,
        "dfs_order_match": dfs_match,
        "distances_from_start": distances,
    }

    if bfs_match and not dfs_match:
        evidence["reason"] = "visit_trace_matches_bfs_only"
        return BfsDfsResult(method="bfs", evidence=evidence)
    if dfs_match and not bfs_match:
        evidence["reason"] = "visit_trace_matches_dfs_only"
        return BfsDfsResult(method="dfs", evidence=evidence)
    if bfs_match and dfs_match:
        evidence["reason"] = "visit_trace_matches_bfs_and_dfs"
        return BfsDfsResult(method="ambiguous", evidence=evidence)
    evidence["reason"] = "visit_trace_matches_neither_bfs_nor_dfs"
    return BfsDfsResult(method="ambiguous", evidence=evidence)


def detect_bfs_dfs(code: str, task: BfsDfsTask) -> BfsDfsResult:
    cls, reachable_method, err = _load_traversal_class(code)
    if cls is None or reachable_method is None:
        return _ambiguous(err or "load_failed", expected_reachable=task.expected_reachable)

    visit_trace: list[str] = []

    def visit_fn(node: str) -> None:
        visit_trace.append(node)

    try:
        traversal = cls(task.graph, task.start, visit_fn)
    except Exception as exc:
        return _ambiguous(
            f"instantiation_failed: {exc}",
            expected_reachable=task.expected_reachable,
            expected_bfs_order=task.expected_bfs_order,
            expected_dfs_order=task.expected_dfs_order,
        )

    try:
        getattr(traversal, reachable_method)()
    except Exception as exc:
        return _ambiguous(
            f"reachable_nodes_failed: {exc}",
            visit_trace=list(visit_trace),
            expected_reachable=task.expected_reachable,
            expected_bfs_order=task.expected_bfs_order,
            expected_dfs_order=task.expected_dfs_order,
        )

    return _classify_trace(visit_trace, task)


def detect_bfs_dfs_file(path: str, *, task_id: str) -> BfsDfsResult:
    tasks_file = project_root() / "data" / "core_v2" / "tasks" / "bfs_dfs_tasks.json"
    tasks_by_id = {t.task_id: t for t in load_bfs_dfs_tasks(tasks_file)}
    if task_id not in tasks_by_id:
        raise ValueError(f"Unknown task_id: {task_id}")
    code = open(path, encoding="utf-8").read()
    return detect_bfs_dfs(code, tasks_by_id[task_id])
