from collections import OrderedDict
import module_x

class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise Exception("Capacity must be positive")
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = module_x.ResourceGuard()

    def get(self, key: int) -> int:
        with self.lock:
            if key not in self.cache:
                return -1
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: int, value: int) -> None:
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)