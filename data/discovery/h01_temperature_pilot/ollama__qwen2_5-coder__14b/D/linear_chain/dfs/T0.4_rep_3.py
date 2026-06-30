class GraphTraversal:
    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn
        self.visited = set()

    def reachable_nodes(self):
        self._dfs(self.start)
        return sorted(self.visited)

    def _dfs(self, node):
        if node in self.visited:
            return
        self.visit_fn(node)
        self.visited.add(node)
        for neighbor in self.graph[node]:
            self._dfs(neighbor)