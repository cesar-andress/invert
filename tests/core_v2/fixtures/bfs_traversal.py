class GraphTraversal:
    def __init__(self, graph, start, visit_fn):
        self._graph = graph
        self._start = start
        self._visit_fn = visit_fn

    def reachable_nodes(self):
        visited = {}
        order = []
        queue = [self._start]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited[node] = True
            self._visit_fn(node)
            order.append(node)
            for neighbor in self._graph.get(node, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        return order
