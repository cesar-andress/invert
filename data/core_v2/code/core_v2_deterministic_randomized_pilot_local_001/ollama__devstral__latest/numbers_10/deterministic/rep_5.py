import random

class ItemProcessor:
    def __init__(self, items, process_fn, seed=None):
        self.items = sorted(items)
        self.process_fn = process_fn
        if seed is not None:
            random.seed(seed)

    def process_all(self):
        processed_items = []
        for item in self.items:
            processed_item = self.process_fn(item)
            processed_items.append(processed_item)
        return sorted(processed_items)
