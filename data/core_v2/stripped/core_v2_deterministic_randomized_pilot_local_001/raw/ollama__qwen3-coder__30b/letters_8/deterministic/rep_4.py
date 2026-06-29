class ItemProcessor:
    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn
        self.seed = seed
        self.processed_items = []
        
    def process_all(self):
        sorted_items = sorted(self.items)
        for item in sorted_items:
            self.processed_items.append(self.process_fn(item))
        return self.processed_items