class x0:

    def __init__(self, x1, x2, x3):
        self.graph = x1
        self.start = x2
        self.visit_fn = x3
        self.visited = x4()

    def x5(self):
        x6 = x7([self.start])
        x8 = []
        while x6:
            x9 = x6.popleft()
            if x9 not in self.visited:
                self.visited.add(x9)
                self.visit_fn(x9)
                x8.append(x9)
                for x10 in self.graph[x9]:
                    if x10 not in self.visited:
                        x6.append(x10)
        return x11(x8)