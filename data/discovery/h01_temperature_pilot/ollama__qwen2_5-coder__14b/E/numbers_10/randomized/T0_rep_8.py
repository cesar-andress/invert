import random

class ItemProcessor:
    def __init__(self, items, visit_fn, seed=None):
        self.items = list(items)
        self.visit_fn = visit_fn
        self.seed = seed

    def process_all(self):
        if self.seed is not None:
            random.seed(self.seed)
        
        randomized_items = self.items[:]
        random.shuffle(randomized_items)
        
        for item in randomized_items:
            self.visit_fn(item)
        
        return sorted(self.items)