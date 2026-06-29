class ItemProcessor:

    def __init__(self, items, visit_fn, seed=None):
        self.items = list(items)
        self.visit_fn = visit_fn
        self.seed = seed

    def process_all(self):
        sorted_items = sorted(self.items)
        for item in sorted_items:
            self.visit_fn(item)
        return sorted_items