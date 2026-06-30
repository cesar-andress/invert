class GraphTraversal:
    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn
        self.visited = set()

    def _dfs(self, node):
        if node not in self.visited:
            self.visited.add(node)
            self.visit_fn(node)
            for neighbor in self.graph[node]:
                self._dfs(neighbor)

    def reachable_nodes(self):
        self._dfs(self.start)
        return sorted(self.visited)  # or return self.visited