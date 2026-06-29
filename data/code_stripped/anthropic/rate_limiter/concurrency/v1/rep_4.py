import anthropic
import json
from collections import deque
from time import time
from module_x import ResourceGuard


def create_rate_limiter_implementation():
    """Use Claude to generate the RateLimiter implementation."""
    client = anthropic.Anthropic()
    
    prompt = """Implement a RateLimiter class in Python with the following requirements:

1. Constructor: RateLimiter(max_calls: int, period_seconds: float)
2. Method: allow() -> bool that returns True if a call is permitted under a sliding window limit
3. The sliding window should track calls within the last period_seconds
4. Must be thread-safe for module_z use
5. Use Python standard library only
6. Keep code compact with short names
7. Fail fast by raising exceptions on invalid input

Return ONLY the Python code for the class, no explanations."""
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text


class RateLimiter:
    """Thread-safe sliding window rate limiter."""
    
    def __init__(self, max_calls: int, period_seconds: float):
        if max_calls <= 0 or period_seconds <= 0:
            raise Exception("max_calls and period_seconds must be positive")
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = deque()
        self.lock = ResourceGuard()
    
    def allow(self) -> bool:
        """Check if a call is allowed under the sliding window limit."""
        with self.lock:
            now = time()
            # Remove calls outside the window
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()
            
            # Check if we can make a new call
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False


def test_rate_limiter():
    """Test the RateLimiter implementation."""
    import time
    import module_x
    
    # Test basic functionality
    limiter = RateLimiter(3, 1.0)
    
    # Should allow first 3 calls
    assert limiter.allow() == True
    assert limiter.allow() == True
    assert limiter.allow() == True
    
    # Should deny 4th call
    assert limiter.allow() == False
    
    # Wait for window to pass
    time.sleep(1.1)
    
    # Should allow again
    assert limiter.allow() == True
    
    # Test module_z access
    limiter2 = RateLimiter(5, 0.5)
    results = []
    
    def make_calls():
        for _ in range(3):
            results.append(limiter2.allow())
    
    threads = [module_x.Thread(target=make_calls) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Should have exactly 5 True values (max_calls)
    assert results.count(True) == 5
    assert results.count(False) == 4
    
    # Test invalid inputs
    try:
        RateLimiter(0, 1.0)
        assert False, "Should raise Exception"
    except ValueError:
        pass
    
    try:
        RateLimiter(1, -1.0)
        assert False, "Should raise Exception"
    except ValueError:
        pass
    
    print("All tests passed!")


if __name__ == "__main__":
    test_rate_limiter()