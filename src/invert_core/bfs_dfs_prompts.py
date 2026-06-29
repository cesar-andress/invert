from __future__ import annotations

from invert_core.bfs_dfs_tasks import BfsDfsTask

BFS_DFS_METHOD_LABELS = {
    "bfs": "Breadth-first graph traversal",
    "dfs": "Depth-first graph traversal",
}

BFS_DFS_METHOD_OPERATIONAL = {
    "bfs": (
        "Implement GraphTraversal.reachable_nodes as breadth-first search. "
        "Use a queue with FIFO behavior. "
        "Call visit_fn(node) exactly when each node is first visited. "
        "Return all reachable nodes from start. "
        "Do not print. No demo code."
    ),
    "dfs": (
        "Implement GraphTraversal.reachable_nodes as depth-first search. "
        "Use recursion or a stack with LIFO behavior. "
        "Call visit_fn(node) exactly when each node is first visited. "
        "Return all reachable nodes from start. "
        "Do not print. No demo code."
    ),
}


def build_bfs_dfs_generation_prompt(
    task: BfsDfsTask, method: str, *, language: str = "python"
) -> str:
    if method not in BFS_DFS_METHOD_LABELS:
        raise ValueError(f"Unknown method: {method}")

    return f"""Write {language} code only.
No explanations.
No markdown.
No code fences.
One self-contained implementation.
Use only the Python standard library.
Do not include demo code or print statements.

Task ID: {task.task_id}
Start node: {task.start}
Graph (adjacency list, neighbor order is significant):
{task.graph}

Required class (exact name and API):

class GraphTraversal:
    def __init__(self, graph, start, visit_fn):
        ...
    def reachable_nodes(self):
        ...

Method label: {BFS_DFS_METHOD_LABELS[method]}
Operational requirement: {BFS_DFS_METHOD_OPERATIONAL[method]}

The generated class must call visit_fn(node) exactly when each node is first visited.
reachable_nodes() must return the set or sorted list of all nodes reachable from start.
"""


def build_bfs_dfs_stub_code(task: BfsDfsTask, method: str) -> str:
    if method == "bfs":
        body = (
            "    def __init__(self, graph, start, visit_fn):\n"
            "        self._graph = graph\n"
            "        self._start = start\n"
            "        self._visit_fn = visit_fn\n"
            "\n"
            "    def reachable_nodes(self):\n"
            "        visited = {}\n"
            "        order = []\n"
            "        queue = [self._start]\n"
            "        while queue:\n"
            "            node = queue.pop(0)\n"
            "            if node in visited:\n"
            "                continue\n"
            "            visited[node] = True\n"
            "            self._visit_fn(node)\n"
            "            order.append(node)\n"
            "            for neighbor in self._graph.get(node, []):\n"
            "                if neighbor not in visited:\n"
            "                    queue.append(neighbor)\n"
            "        return order\n"
        )
    else:
        body = (
            "    def __init__(self, graph, start, visit_fn):\n"
            "        self._graph = graph\n"
            "        self._start = start\n"
            "        self._visit_fn = visit_fn\n"
            "\n"
            "    def reachable_nodes(self):\n"
            "        visited = {}\n"
            "        order = []\n"
            "        stack = [self._start]\n"
            "        while stack:\n"
            "            node = stack.pop()\n"
            "            if node in visited:\n"
            "                continue\n"
            "            visited[node] = True\n"
            "            self._visit_fn(node)\n"
            "            order.append(node)\n"
            "            neighbors = self._graph.get(node, [])\n"
            "            pending = []\n"
            "            for n in neighbors:\n"
            "                pending.append(n)\n"
            "            while pending:\n"
            "                neighbor = pending.pop()\n"
            "                if neighbor not in visited:\n"
            "                    stack.append(neighbor)\n"
            "        return order\n"
        )
    return f"# Stub {method} for {task.task_id}\nclass GraphTraversal:\n{body}"
