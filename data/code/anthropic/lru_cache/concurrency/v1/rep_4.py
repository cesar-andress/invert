import anthropic
from threading import Lock
from collections import OrderedDict


def create_lru_cache_implementation():
    """Use Claude to generate an LRU cache implementation."""
    client = anthropic.Anthropic()
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": """Generate a Python LRU Cache class implementation with the following requirements:
1. Methods: get(key) and put(key, value)
2. Fixed capacity support
3. get() returns -1 for missing keys
4. Both operations must be O(1) average time
5. Thread-safe for concurrent use
6. Use Python standard library utilities
7. Compact code with short names
8. Fail fast with exceptions on invalid input

Return only the Python class code, no explanations."""
            }
        ]
    )
    
    return message.content[0].text


class LRUCache:
    """Thread-safe LRU Cache with O(1) get and put operations."""
    
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.cap = capacity
        self.cache = OrderedDict()
        self.lock = Lock()
    
    def get(self, key):
        """Get value for key, return -1 if not found. O(1) operation."""
        with self.lock:
            if key not in self.cache:
                return -1
            self.cache.move_to_end(key)
            return self.cache[key]
    
    def put(self, key, value):
        """Put key-value pair, evict LRU item if at capacity. O(1) operation."""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.cache[key] = value
            else:
                if len(self.cache) >= self.cap:
                    self.cache.popitem(last=False)
                self.cache[key] = value


if __name__ == "__main__":
    cache = LRUCache(2)
    
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    
    cache.put(3, 3)
    assert cache.get(2) == -1
    
    cache.put(4, 4)
    assert cache.get(1) == -1
    assert cache.get(3) == 3
    assert cache.get(4) == 4
    
    print("All tests passed!")