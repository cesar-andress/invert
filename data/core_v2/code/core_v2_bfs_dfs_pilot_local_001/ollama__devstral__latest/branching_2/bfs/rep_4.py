from collections import deque

class GraphTraversal:
    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn
        self.visited = set()

    def reachable_nodes(self):
        queue = deque([self.start])
        result = []

        while queue:
            node = queue.popleft()
            if node not in self.visited:
                self.visited.add(node)
                self.visit_fn(node)
                result.append(node)
                for neighbor in self.graph[node]:
                    if neighbor not in self.visited:
                        queue.append(neighbor)

        return sorted(result)
