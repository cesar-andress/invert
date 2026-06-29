class ItemProcessor:

    def __init__(self, items, visit_fn, seed=None):
        self.items = list(items)
        self.visit_fn = visit_fn
        self.seed = seed

    def process_all(self):
        for x0 in sorted(self.items):
            self.visit_fn(x0)
        return sorted(self.items)