class GraphTraversal:

    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn

    def reachable_nodes(self):
        x0 = set()
        x1 = [self.start]
        x0.add(self.start)
        self.visit_fn(self.start)
        x2 = [self.start]
        while x1:
            x3 = x1.pop(0)
            for x4 in self.graph[x3]:
                if x4 not in x0:
                    x0.add(x4)
                    self.visit_fn(x4)
                    x1.append(x4)
                    x2.append(x4)
        return x2