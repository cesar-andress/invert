import random

class ItemProcessor:
    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        self.seed = seed

    def process_all(self):
        if self.seed is not None:
            random.seed(self.seed)
        
        processed_items = []
        for item in random.sample(self.items, len(self.items)):
            processed_items.append(self.process_fn(item))
        
        return sorted(processed_items)