class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        self.seed = seed

    def process_all(self):
        import random
        x0 = self.items[:]
        if self.seed is not None:
            random.seed(self.seed)
        random.shuffle(x0)
        x1 = []
        for x2 in x0:
            x1.append(self.process_fn(x2))
        return sorted(x1) if isinstance(x1[0], (int, float)) else set(x1)