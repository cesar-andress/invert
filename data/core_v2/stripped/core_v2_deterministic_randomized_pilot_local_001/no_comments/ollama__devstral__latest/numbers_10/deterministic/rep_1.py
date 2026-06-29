class ItemProcessor:

    def __init__(self, items, process_fn, seed=None):
        self.items = sorted(items)
        self.process_fn = process_fn

    def process_all(self):
        result = []
        for item in self.items:
            processed_item = self.process_fn(item)
            result.append(processed_item)
        return result