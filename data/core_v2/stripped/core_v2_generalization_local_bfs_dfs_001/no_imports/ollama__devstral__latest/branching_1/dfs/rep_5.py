class GraphTraversal:

    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn

    def reachable_nodes(self):
        x0 = set()
        x1 = []

        def x2(x3):
            if x3 not in x0:
                x0.add(x3)
                self.visit_fn(x3)
                x1.append(x3)
                for x4 in self.graph[x3]:
                    x2(x4)
        x2(self.start)
        return sorted(x1)