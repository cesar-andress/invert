import random

class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = items[:]
        self.process_fn = process_fn
        if seed is not None:
            random.seed(seed)

    def process_all(self):
        random.shuffle(self.items)
        processed_items = set()
        for item in self.items:
            processed_item = self.process_fn(item)
            processed_items.add(processed_item)
        return sorted(processed_items)