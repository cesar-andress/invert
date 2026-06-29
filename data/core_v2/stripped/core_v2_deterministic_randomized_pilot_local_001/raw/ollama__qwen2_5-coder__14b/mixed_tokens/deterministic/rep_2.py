class ItemProcessor:
    def __init__(self, items, process_fn, seed=None):
        self.items = items
        self.process_fn = process_fn

    def process_all(self):
        processed_items = []
        for item in sorted(self.items):
            processed_item = self.process_fn(item)
            processed_items.append(processed_item)
        return set(processed_items)