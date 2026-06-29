class GraphTraversal:

    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn

    def reachable_nodes(self):
        visited = set()
        stack = [self.start]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                self.visit_fn(node)
                for neighbor in reversed(self.graph[node]):
                    if neighbor not in visited:
                        stack.append(neighbor)
        return sorted(visited)