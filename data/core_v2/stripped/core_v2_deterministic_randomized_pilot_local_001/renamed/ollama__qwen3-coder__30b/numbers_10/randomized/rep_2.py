class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        self.seed = seed

    def process_all(self):
        import random
        x0 = random.Random(self.seed)
        x1 = self.items[:]
        x0.shuffle(x1)
        x2 = []
        for x3 in x1:
            x2.append(self.process_fn(x3))
        return sorted(x2) if isinstance(x2[0], (int, float)) else set(x2)