import random


class ItemProcessor:
    def __init__(self, items, visit_fn, seed=None):
        self.items = list(items)
        self.visit_fn = visit_fn
        self.seed = seed
        self._rng = random.Random(seed)

    def process_all(self):
        order = list(self.items)
        self._rng.shuffle(order)
        for item in order:
            self.visit_fn(item)
        return sorted(self.items, key=str)
