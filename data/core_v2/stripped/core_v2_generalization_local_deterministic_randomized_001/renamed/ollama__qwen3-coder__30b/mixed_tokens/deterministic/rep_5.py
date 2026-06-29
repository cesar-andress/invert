class ItemProcessor:

    def __init__(self, items, visit_fn, seed=None):
        self.items = list(items)
        self.visit_fn = visit_fn
        self.seed = seed

    def process_all(self):
        x0 = sorted(self.items)
        for x1 in x0:
            self.visit_fn(x1)
        return x0