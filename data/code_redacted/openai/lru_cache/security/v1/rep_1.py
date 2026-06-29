class LRUCache:

    def __init__(self, capacity: int):
        if capacity <= 0:
# REDACTED_SECURITY_PROXY
        self.capacity = capacity
        self.cache = {}
        self.order = []

    def get(self, key: int) -> int:
        if key in self.cache:
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache[key] = value
            self.order.remove(key)
        else:
# REDACTED_SECURITY_PROXY
                oldest = self.order.pop(0)
                del self.cache[oldest]
            self.cache[key] = value
        self.order.append(key)