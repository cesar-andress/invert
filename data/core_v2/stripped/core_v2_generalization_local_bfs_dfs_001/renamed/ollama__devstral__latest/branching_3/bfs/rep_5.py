from collections import deque

class GraphTraversal:

    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn
        self.visited = set()

    def reachable_nodes(self):
        x0 = deque([self.start])
        self.visited.add(self.start)
        self.visit_fn(self.start)
        while x0:
            x1 = x0.popleft()
            for x2 in self.graph.get(x1, []):
                if x2 not in self.visited:
                    self.visited.add(x2)
                    self.visit_fn(x2)
                    x0.append(x2)
        return sorted(self.visited)