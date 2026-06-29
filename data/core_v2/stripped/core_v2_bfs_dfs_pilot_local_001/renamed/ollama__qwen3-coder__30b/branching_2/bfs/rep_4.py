class x0:

    def __init__(self, x1, x2, x3):
        self.graph = x1
        self.start = x2
        self.visit_fn = x3

    def x4(self):
        x5 = x6()
        x7 = [self.start]
        x5.add(self.start)
        self.visit_fn(self.start)
        x8 = [self.start]
        while x7:
            x9 = x7.pop(0)
            for x10 in self.graph[x9]:
                if x10 not in x5:
                    x5.add(x10)
                    self.visit_fn(x10)
                    x7.append(x10)
                    x8.append(x10)
        return x8