import anthropic
import json
from collections import deque
from time import time
# REDACTED_CONCURRENCY_PROXY


def create_rate_limiter_implementation():
    """Use Claude to generate the RateLimiter implementation."""
    client = anthropic.Anthropic()
    
    prompt = """Create a Python RateLimiter class with the following specifications:

1. Constructor: RateLimiter(max_calls: int, period_seconds: float)
2. Method: allow() -> bool
   - Returns True if a call is permitted under a sliding window limit
   - Returns False if the limit has been exceeded
3. Requirements:
   - Use a sliding window algorithm (not fixed windows)
# REDACTED_CONCURRENCY_PROXY
   - Use Python standard library only
   - Compact code with short names
   - Fail fast with exceptions on invalid input

The sliding window should track timestamps of recent calls and allow a call only if 
the number of calls in the last period_seconds is less than max_calls.

Return ONLY the Python code for the class, no explanations."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text


def extract_code_from_response(response_text):
    """Extract Python code from Claude's response."""
    if "