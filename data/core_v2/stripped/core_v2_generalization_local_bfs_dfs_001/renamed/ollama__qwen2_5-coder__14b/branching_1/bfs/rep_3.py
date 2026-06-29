from collections import deque

class GraphTraversal:

    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn

    def reachable_nodes(self):
        x0 = set()
        x1 = deque([self.start])
        while x1:
            x2 = x1.popleft()
            if x2 not in x0:
                x0.add(x2)
                self.visit_fn(x2)
                for x3 in self.graph[x2]:
                    if x3 not in x0:
                        x1.append(x3)
        return sorted(x0)