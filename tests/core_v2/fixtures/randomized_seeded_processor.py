import random


class ItemProcessor:
    def __init__(self, items, process_fn, seed=None):
        self._items = list(items)
        self._process_fn = process_fn
        self._rng = random.Random(seed)

    def process_all(self):
        order = list(self._items)
        self._rng.shuffle(order)
        for item in order:
            self._process_fn(item)
        return sorted(self._items, key=str)
