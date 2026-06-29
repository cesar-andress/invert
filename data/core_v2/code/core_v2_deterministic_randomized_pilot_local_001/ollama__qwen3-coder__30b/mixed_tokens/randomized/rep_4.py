class ItemProcessor:
    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        self.seed = seed
    
    def process_all(self):
        import random
        rng = random.Random(self.seed)
        shuffled_items = self.items[:]
        rng.shuffle(shuffled_items)
        processed = [self.process_fn(item) for item in shuffled_items]
        return processed
