class ItemProcessor:
    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        self.seed = seed
    
    def process_all(self):
        import random
        items_copy = self.items[:]
        if self.seed is not None:
            random.seed(self.seed)
        random.shuffle(items_copy)
        results = []
        for item in items_copy:
            results.append(self.process_fn(item))
        return sorted(results) if isinstance(results[0], (int, float)) else set(results)
