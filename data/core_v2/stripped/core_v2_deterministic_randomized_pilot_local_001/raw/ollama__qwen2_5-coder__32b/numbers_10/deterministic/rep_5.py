class ItemProcessor:
    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn

    def process_all(self):
        processed_items = [self.process_fn(item) for item in sorted(self.items)]
        return processed_items