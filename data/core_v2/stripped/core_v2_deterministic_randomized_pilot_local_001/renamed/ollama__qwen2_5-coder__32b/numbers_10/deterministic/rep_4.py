class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn

    def process_all(self):
        x0 = [self.process_fn(x1) for x1 in sorted(self.items)]
        return x0