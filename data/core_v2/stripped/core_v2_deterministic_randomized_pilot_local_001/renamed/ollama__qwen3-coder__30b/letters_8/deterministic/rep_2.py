class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        self.seed = seed
        self.processed_items = []

    def process_all(self):
        x0 = sorted(self.items)
        for x1 in x0:
            self.processed_items.append(self.process_fn(x1))
        return self.processed_items