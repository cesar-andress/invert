class GraphTraversal:
    def __init__(self, graph, start, visit_fn):
        self._graph = graph
        self._start = start
        self._visit_fn = visit_fn

    def reachable_nodes(self):
        visited = {}
        order = []
        stack = [self._start]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited[node] = True
            self._visit_fn(node)
            order.append(node)
            neighbors = self._graph.get(node, [])
            pending = []
            for n in neighbors:
                pending.append(n)
            while pending:
                neighbor = pending.pop()
                if neighbor not in visited:
                    stack.append(neighbor)
        return order
