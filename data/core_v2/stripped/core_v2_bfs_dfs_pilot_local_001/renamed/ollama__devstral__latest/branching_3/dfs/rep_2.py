class x0:

    def __init__(self, x1, x2, x3):
        self.graph = x1
        self.start = x2
        self.visit_fn = x3

    def x4(self):
        x5 = x6()
        x7 = [self.start]
        while x7:
            x8 = x7.pop()
            if x8 not in x5:
                x5.add(x8)
                self.visit_fn(x8)
                for x9 in x10(self.graph.get(x8, [])):
                    if x9 not in x5:
                        x7.append(x9)
        return x11(x5)