import anthropic
import time
from collections import deque


def create_rate_limiter():
    """Create a RateLimiter class using Claude to generate the implementation."""
    client = anthropic.Anthropic()
    
    prompt = """Implement a RateLimiter class with the following specifications:

1. Constructor: RateLimiter(max_calls: int, period_seconds: float)
2. Method: allow() -> bool
   - Returns True if a call is permitted under a sliding window limit
   - The limit is max_calls within period_seconds
   - Uses a sliding window approach (not fixed buckets)

Requirements:
- Use Python standard library only
- Single-threaded execution
- Compact code with short names
- Fail fast with exceptions on invalid input
- No explicit input validation needed (assume well-formed inputs)

Return only the Python class implementation, no explanations."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text


# Get the implementation from Claude
implementation = create_rate_limiter()

# Execute the implementation to define the class
exec(implementation)

# Test the RateLimiter
if __name__ == "__main__":
    # Test 1: Basic functionality
    limiter = RateLimiter(max_calls=3, period_seconds=1.0)
    
    # Should allow first 3 calls
    assert limiter.allow() == True, "First call should be allowed"
    assert limiter.allow() == True, "Second call should be allowed"
    assert limiter.allow() == True, "Third call should be allowed"
    assert limiter.allow() == False, "Fourth call should be denied"
    
    # Test 2: Sliding window - after period expires
    time.sleep(1.1)
    assert limiter.allow() == True, "Call after period should be allowed"
    
    # Test 3: Multiple calls within period
    limiter2 = RateLimiter(max_calls=2, period_seconds=0.5)
    assert limiter2.allow() == True
    assert limiter2.allow() == True
    assert limiter2.allow() == False
    time.sleep(0.3)
    assert limiter2.allow() == False  # Still within window
    time.sleep(0.3)
    assert limiter2.allow() == True  # Window expired
    
    print("All tests passed!")