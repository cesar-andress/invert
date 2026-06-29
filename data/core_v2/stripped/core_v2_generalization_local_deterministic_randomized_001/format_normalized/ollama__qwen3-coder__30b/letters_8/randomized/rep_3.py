class ItemProcessor:

    def __init__(self, items, visit_fn, seed=None):
        self.items = list(items)
        self.visit_fn = visit_fn
        self.seed = seed

    def process_all(self):
        random = __import__('random')
        x0 = random.Random(self.seed)
        x1 = self.items[:]
        x0.shuffle(x1)
        for x2 in x1:
            self.visit_fn(x2)
        return sorted(self.items) if isinstance(self.items[0], str) else set(self.items)