class x0:

    def __init__(self, x1, x2, x3):
        self.graph = x1
        self.start = x2
        self.visit_fn = x3

    def x4(self):
        x5 = x6([self.start])
        x7 = x8()
        while x5:
            x9 = x5.popleft()
            if x9 not in x7:
                x7.add(x9)
                self.visit_fn(x9)
                for x10 in self.graph[x9]:
                    if x10 not in x7:
                        x5.append(x10)
        return x11(x7)