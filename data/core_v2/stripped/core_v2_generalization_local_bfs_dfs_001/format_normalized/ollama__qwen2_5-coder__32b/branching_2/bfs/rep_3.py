class GraphTraversal:

    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn

    def reachable_nodes(self):
        deque = __import__('collections', fromlist=['deque']).deque
        x0 = deque([self.start])
        x1 = set()
        while x0:
            x2 = x0.popleft()
            if x2 not in x1:
                x1.add(x2)
                self.visit_fn(x2)
                for x3 in self.graph[x2]:
                    if x3 not in x1:
                        x0.append(x3)
        return sorted(x1)