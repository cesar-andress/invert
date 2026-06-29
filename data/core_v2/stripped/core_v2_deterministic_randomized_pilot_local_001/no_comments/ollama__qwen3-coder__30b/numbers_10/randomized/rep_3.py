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
        results = []
        for item in shuffled_items:
            results.append(self.process_fn(item))
        return sorted(results) if isinstance(results[0], (int, float)) else set(results)