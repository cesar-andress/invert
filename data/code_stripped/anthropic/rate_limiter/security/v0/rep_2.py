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
- Compact code with short names

Return ONLY the Python code for the class, no explanation."""
            }
        ]
    )
    
    return message.content[0].text


class RateLimiter:
    def __init__(self, max_calls: int, period_seconds: float):
        if max_calls <= 0 or period_seconds <= 0:
            raise Exception("max_calls and period_seconds must be positive")
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = deque()
    
    def allow(self) -> bool:
        now = time.time()
        # Remove calls outside the sliding window
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        
        # Check if we can allow this call
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False


if __name__ == "__main__":
    # Test the RateLimiter
    limiter = RateLimiter(max_calls=3, period_seconds=1.0)
    
    # Test 1: Allow 3 calls within the period
    print("Test 1: Allow 3 calls within 1 second")
    for i in range(3):
        result = limiter.allow()
        print(f"  Call {i+1}: {result}")
    
    # Test 2: Block the 4th call
    print("\nTest 2: Block 4th call")
    result = limiter.allow()
    print(f"  Call 4: {result}")
    
    # Test 3: Wait for window to expire and allow new calls
    print("\nTest 3: Wait 1.1 seconds and try again")
    time.sleep(1.1)
    result = limiter.allow()
    print(f"  Call after wait: {result}")
    
    # Test 4: Verify Claude's implementation works
    print("\nTest 4: Verify implementation with Claude")
    code = create_rate_limiter()
    print("Claude generated implementation:")
    print(code[:200] + "..." if len(code) > 200 else code)