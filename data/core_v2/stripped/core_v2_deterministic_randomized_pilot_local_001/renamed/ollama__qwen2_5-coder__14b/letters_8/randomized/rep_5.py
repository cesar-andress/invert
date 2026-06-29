import random

class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        self.seed = seed

    def process_all(self):
        if self.seed is not None:
            random.seed(self.seed)
        x0 = []
        for x1 in random.sample(self.items, len(self.items)):
            x0.append(self.process_fn(x1))
        return sorted(x0)