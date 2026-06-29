from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class BfsDfsTask:
    task_id: str
    graph: dict[str, list[str]]
    start: str
    expected_reachable: list[str]
    control_family: str = "branching"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BfsDfsTask:
        return cls(
            task_id=data["task_id"],
            graph={k: list(v) for k, v in data["graph"].items()},
            start=data["start"],
            expected_reachable=list(data["expected_reachable"]),
            control_family=data.get("control_family", "branching"),
        )

    @property
    def expected_bfs_order(self) -> list[str]:
        return compute_bfs_order(self.graph, self.start)

    @property
    def expected_dfs_order(self) -> list[str]:
        return compute_dfs_preorder(self.graph, self.start)

    @property
    def is_negative_control(self) -> bool:
        return self.control_family == "linear_chain"


def compute_bfs_order(graph: dict[str, list[str]], start: str) -> list[str]:
    visited: set[str] = set()
    order: list[str] = []
    queue: deque[str] = deque([start])
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                queue.append(neighbor)
    return order


def compute_dfs_preorder(graph: dict[str, list[str]], start: str) -> list[str]:
    visited: set[str] = set()
    order: list[str] = []

    def dfs(node: str) -> None:
        if node in visited:
            return
        visited.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor)

    dfs(start)
    return order


def load_bfs_dfs_tasks(path: Path | str) -> list[BfsDfsTask]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [BfsDfsTask.from_dict(item) for item in raw["tasks"]]


def filter_bfs_dfs_tasks(tasks: list[BfsDfsTask], task_ids: list[str]) -> list[BfsDfsTask]:
    by_id = {t.task_id: t for t in tasks}
    missing = [tid for tid in task_ids if tid not in by_id]
    if missing:
        raise ValueError(f"Unknown task IDs: {missing}")
    return [by_id[tid] for tid in task_ids]


def bfs_dfs_distances(graph: dict[str, list[str]], start: str) -> dict[str, int]:
    distances: dict[str, int] = {start: 0}
    queue: deque[str] = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)
    return distances
