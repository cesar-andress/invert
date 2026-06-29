random = __import__('random')

class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        if seed is not None:
            random.seed(seed)

    def process_all(self):
        x0 = []
        x1 = list(self.items)
        random.shuffle(x1)
        for x2 in x1:
            x0.append(self.process_fn(x2))
        return sorted(x0)