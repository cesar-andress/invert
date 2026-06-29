class ItemProcessor:
    def __init__(self, items, process_fn, seed=None):
        self._items = list(items)
        self._process_fn = process_fn
        self._seed = seed

    def process_all(self):
        ordered = sorted(self._items, key=str)
        for item in ordered:
            self._process_fn(item)
        return sorted(self._items, key=str)
