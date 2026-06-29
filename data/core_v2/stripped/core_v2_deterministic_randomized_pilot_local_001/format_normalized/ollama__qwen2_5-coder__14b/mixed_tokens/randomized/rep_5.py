random = __import__('random')

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
            x2 = self.process_fn(x1)
            x0.append(x2)
        return sorted(x0)