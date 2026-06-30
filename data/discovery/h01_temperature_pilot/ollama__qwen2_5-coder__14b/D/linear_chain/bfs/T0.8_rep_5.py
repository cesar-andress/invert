from collections import deque

class GraphTraversal:
    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn

    def reachable_nodes(self):
        visited = set()
        queue = deque([self.start])

        while queue:
            node = queue.popleft()
            if node not in visited:
                self.visit_fn(node)
                visited.add(node)
                queue.extend(neighbor for neighbor in self.graph[node] if neighbor not in visited)

        return list(sorted(visited))