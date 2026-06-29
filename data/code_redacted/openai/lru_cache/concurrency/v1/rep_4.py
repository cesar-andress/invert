from collections import OrderedDict
# REDACTED_CONCURRENCY_PROXY

class LRUCache:

    def __init__(self, capacity: int):
        if capacity <= 0:
# REDACTED_SECURITY_PROXY
        self.capacity = capacity
        self.cache = OrderedDict()
# REDACTED_CONCURRENCY_PROXY

    def get(self, key: int) -> int:
# REDACTED_CONCURRENCY_PROXY
            if key not in self.cache:
                return -1
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: int, value: int) -> None:
# REDACTED_CONCURRENCY_PROXY
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
# REDACTED_SECURITY_PROXY
                self.cache.popitem(last=False)