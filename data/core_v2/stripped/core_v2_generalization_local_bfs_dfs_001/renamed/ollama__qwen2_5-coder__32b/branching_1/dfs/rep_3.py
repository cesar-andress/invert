class GraphTraversal:

    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn

    def reachable_nodes(self):
        x0 = set()

        def x1(x2):
            if x2 not in x0:
                x0.add(x2)
                self.visit_fn(x2)
                for x3 in self.graph[x2]:
                    x1(x3)
        x1(self.start)
        return sorted(x0)