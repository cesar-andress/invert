class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        self.seed = seed

    def process_all(self):
        sorted_items = sorted(self.items)
        results = []
        for item in sorted_items:
            results.append(self.process_fn(item))
        return results