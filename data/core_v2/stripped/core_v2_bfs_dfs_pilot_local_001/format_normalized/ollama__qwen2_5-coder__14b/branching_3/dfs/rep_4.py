class x0:

    def __init__(self, x1, x2, x3):
        self.graph = x1
        self.start = x2
        self.visit_fn = x3
        self.visited = x4()

    def x5(self):

        def x6(x7):
            if x7 not in self.visited:
                self.visited.add(x7)
                self.visit_fn(x7)
                for x8 in self.graph[x7]:
                    x6(x8)
        x6(self.start)
        return x9(self.visited)