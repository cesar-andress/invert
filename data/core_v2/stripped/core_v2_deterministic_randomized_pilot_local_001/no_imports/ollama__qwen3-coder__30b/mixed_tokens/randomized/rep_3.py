class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        self.seed = seed

    def process_all(self):
        random = __import__('random')
        x0 = random.Random(self.seed)
        x1 = self.items[:]
        x0.shuffle(x1)
        x2 = [self.process_fn(x3) for x3 in x1]
        return x2