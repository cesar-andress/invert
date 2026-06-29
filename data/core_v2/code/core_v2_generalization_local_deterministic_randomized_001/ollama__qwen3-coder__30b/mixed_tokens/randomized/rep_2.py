class ItemProcessor:
    def __init__(self, items, visit_fn, seed=None):
        self.items = list(items)
        self.visit_fn = visit_fn
        self.seed = seed

    def process_all(self):
        import random
        rng = random.Random(self.seed)
        shuffled = self.items[:]
        rng.shuffle(shuffled)
        for item in shuffled:
            self.visit_fn(item)
        return sorted(self.items) if isinstance(self.items, list) else set(self.items)
