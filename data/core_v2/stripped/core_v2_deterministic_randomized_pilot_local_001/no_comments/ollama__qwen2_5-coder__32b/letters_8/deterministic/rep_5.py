class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn

    def process_all(self):
        processed_items = []
        for item in sorted(self.items):
            processed_items.append(self.process_fn(item))
        return processed_items