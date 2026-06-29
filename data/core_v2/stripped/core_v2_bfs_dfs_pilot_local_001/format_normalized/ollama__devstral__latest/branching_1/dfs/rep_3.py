class x0:

    def __init__(self, x1, x2, x3):
        self.graph = x1
        self.start = x2
        self.visit_fn = x3

    def x4(self):
        x5 = x6()
        x7 = []

        def x8(x9):
            if x9 not in x5:
                x5.add(x9)
                self.visit_fn(x9)
                x7.append(x9)
                for x10 in self.graph[x9]:
                    x8(x10)
        x8(self.start)
        return x11(x7)