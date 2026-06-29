from collections import deque

class x0:

    def __init__(self, x1, x2, x3):
        self.graph = x1
        self.start = x2
        self.visit_fn = x3
        self.visited = x4()

    def x5(self):
        x6 = x7([self.start])
        self.visited.add(self.start)
        self.visit_fn(self.start)
        while x6:
            x8 = x6.popleft()
            for x9 in self.graph.get(x8, []):
                if x9 not in self.visited:
                    self.visited.add(x9)
                    self.visit_fn(x9)
                    x6.append(x9)
        return x10(self.visited)