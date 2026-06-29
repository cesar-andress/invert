import random

class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        if seed is not None:
            random.seed(seed)

    def process_all(self):
        processed_items = []
        shuffled_items = list(self.items)
        random.shuffle(shuffled_items)
        for item in shuffled_items:
            processed_items.append(self.process_fn(item))
        return sorted(processed_items)