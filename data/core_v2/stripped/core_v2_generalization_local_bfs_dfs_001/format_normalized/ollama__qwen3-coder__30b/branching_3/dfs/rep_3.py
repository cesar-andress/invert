class GraphTraversal:

    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn
        self.visited = set()

    def reachable_nodes(self):

        def x0(x1):
            if x1 not in self.visited:
                self.visited.add(x1)
                self.visit_fn(x1)
                for x2 in self.graph[x1]:
                    x0(x2)
        x0(self.start)
        return list(self.visited)