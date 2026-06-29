random = __import__('random')

class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = sorted(items)
        self.process_fn = process_fn
        if seed is not None:
            random.seed(seed)

    def process_all(self):
        x0 = []
        for x1 in self.items:
            x2 = self.process_fn(x1)
            x0.append(x2)
        return sorted(x0)