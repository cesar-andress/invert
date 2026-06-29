class ItemProcessor:
    def __init__(self, items, process_fn):
        self._items = items
        self._process_fn = process_fn

    def process_all(self):
        for item in self._items:
            self._process_fn(item)
            self._process_fn(item)
        return list(self._items)
