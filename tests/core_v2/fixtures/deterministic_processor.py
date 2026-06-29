class ItemProcessor:
    def __init__(self, items, visit_fn, seed=None):
        self.items = list(items)
        self.visit_fn = visit_fn
        self.seed = seed

    def process_all(self):
        ordered = sorted(self.items, key=str)
        for item in ordered:
            self.visit_fn(item)
        return sorted(self.items, key=str)
