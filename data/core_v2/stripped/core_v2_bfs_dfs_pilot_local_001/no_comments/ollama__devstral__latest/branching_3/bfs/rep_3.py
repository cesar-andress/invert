from collections import deque

class GraphTraversal:

    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn
        self.visited = set()

    def reachable_nodes(self):
        queue = deque([self.start])
        self.visited.add(self.start)
        self.visit_fn(self.start)
        while queue:
            node = queue.popleft()
            for neighbor in self.graph.get(node, []):
                if neighbor not in self.visited:
                    self.visited.add(neighbor)
                    self.visit_fn(neighbor)
                    queue.append(neighbor)
        return sorted(self.visited)