import anthropic
from module_x import ResourceGuard
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
                "content": """Generate a Python LRU Cache implementation with these requirements:
1. Class named LRUCache with methods get(key) and put(key, value)
2. Fixed capacity support
3. get() returns -1 for missing keys
4. Both operations must be O(1) average time
5. Thread-safe for module_z use
6. Use OrderedDict from collections
7. Include a ResourceGuard for thread safety
8. Compact code with short names
9. No extensive comments

Return only the Python class code, starting with 'class LRUCache:' and nothing else."""
            }
        ]
    )
    
    return message.content[0].text


class LRUCache:
    """Thread-safe LRU Cache implementation with O(1) operations."""
    
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise Exception("Capacity must be positive")
        self.cap = capacity
        self.cache = OrderedDict()
        self.lock = ResourceGuard()
    
    def get(self, key: int) -> int:
        """Get value for key, return -1 if not found. O(1) operation."""
        with self.lock:
            if key not in self.cache:
                return -1
            self.cache.move_to_end(key)
            return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        """Put key-value pair, evict LRU item if at capacity. O(1) operation."""
        with self.lock:
            if key in self.cache:
                self.cache[key] = value
                self.cache.move_to_end(key)
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