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
- Return False otherwise
- Use collections.deque for efficient timestamp tracking
- Single-threaded execution assumed
- Compact code with minimal comments

Return ONLY the Python class code, no explanations."""
            }
        ]
    )
    
    return message.content[0].text


class RateLimiter:
    def __init__(self, max_calls: int, period_seconds: float):
        if max_calls <= 0 or period_seconds <= 0:
            raise ValueError("max_calls and period_seconds must be positive")
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = deque()
    
    def allow(self) -> bool:
        now = time.time()
        cutoff = now - self.period_seconds
        
        while self.calls and self.calls[0] <= cutoff:
            self.calls.popleft()
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False


if __name__ == "__main__":
    limiter = RateLimiter(max_calls=3, period_seconds=1.0)
    
    print("Testing RateLimiter with max_calls=3, period_seconds=1.0")
    
    for i in range(5):
        result = limiter.allow()
        print(f"Call {i+1}: {result}")
    
    print("\nWaiting 1.1 seconds...")
    time.sleep(1.1)
    
    print("After window expires:")
    for i in range(3):
        result = limiter.allow()
        print(f"Call {i+1}: {result}")