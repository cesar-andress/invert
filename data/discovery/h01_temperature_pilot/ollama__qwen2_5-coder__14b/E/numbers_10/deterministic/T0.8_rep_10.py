class ItemProcessor:
    def __init__(self, items, visit_fn, seed=None):
        self.items = list(items)
        self.visit_fn = visit_fn
        self.seed = seed

    def process_all(self):
        for item in sorted(self.items):
            self.visit_fn(item)
        return sorted(self.items)