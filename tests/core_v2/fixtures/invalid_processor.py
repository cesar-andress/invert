class ItemProcessor:
    def __init__(self, items, visit_fn):
        self.items = items
        self.visit_fn = visit_fn

    def process_all(self):
        for item in self.items:
            self.visit_fn(item)
            self.visit_fn(item)
        return list(self.items)
