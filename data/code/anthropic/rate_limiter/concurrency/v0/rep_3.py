import anthropic
import time
from collections import deque


def create_rate_limiter():
    """Create a RateLimiter class using Claude to generate the implementation."""
    client = anthropic.Anthropic()
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": """Implement a Python class RateLimiter with:
- __init__(self, max_calls: int, period_seconds: float)
- allow(self) -> bool method

The allow() method should return True if a call is permitted under a sliding window rate limit of max_calls within period_seconds.

Requirements:
- Use a sliding window approach (not fixed windows)
- Track timestamps of calls
- Remove old timestamps outside the window
- Return True if call count in window < max_calls
- Increment call count on True return
- Single-threaded, no thread safety needed
- Use standard library only
- Compact implementation

Return only the Python class code, no explanations."""
            }
        ]
    )
    
    return message.content[0].text


class RateLimiter:
    """Rate limiter using sliding window approach."""
    
    def __init__(self, max_calls: int, period_seconds: float):
        if max_calls <= 0 or period_seconds <= 0:
            raise ValueError("max_calls and period_seconds must be positive")
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = deque()
    
    def allow(self) -> bool:
        """Check if a call is allowed under the rate limit."""
        now = time.time()
        
        # Remove calls outside the sliding window
        while self.calls and self.calls[0] < now - self.period_seconds:
            self.calls.popleft()
        
        # Check if we can make another call
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False


def test_rate_limiter():
    """Test the RateLimiter implementation."""
    # Test 1: Basic functionality
    limiter = RateLimiter(3, 1.0)
    
    # Should allow first 3 calls
    assert limiter.allow() == True
    assert limiter.allow() == True
    assert limiter.allow() == True
    
    # Should deny 4th call within window
    assert limiter.allow() == False
    
    # Wait for window to expire
    time.sleep(1.1)
    
    # Should allow call after window expires
    assert limiter.allow() == True
    
    # Test 2: Edge case with very small period
    limiter2 = RateLimiter(2, 0.1)
    assert limiter2.allow() == True
    assert limiter2.allow() == True
    assert limiter2.allow() == False
    
    time.sleep(0.11)
    assert limiter2.allow() == True
    
    # Test 3: Single call limit
    limiter3 = RateLimiter(1, 0.5)
    assert limiter3.allow() == True
    assert limiter3.allow() == False
    
    time.sleep(0.51)
    assert limiter3.allow() == True
    
    print("All tests passed!")


if __name__ == "__main__":
    test_rate_limiter()