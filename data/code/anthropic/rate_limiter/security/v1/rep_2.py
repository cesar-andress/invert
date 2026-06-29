import anthropic
import json
from collections import deque
from time import time


def create_rate_limiter_implementation():
    """Use Claude to generate the RateLimiter implementation."""
    client = anthropic.Anthropic()
    
    prompt = """Generate a Python class RateLimiter with the following specifications:

1. Constructor: __init__(self, max_calls: int, period_seconds: float)
2. Method: allow(self) -> bool
   - Returns True if a call is permitted under a sliding window limit
   - Returns False if the limit has been exceeded
   - Uses a sliding window approach (not fixed buckets)

Requirements:
- Validate inputs: max_calls must be positive integer, period_seconds must be positive number
- Raise ValueError for invalid inputs
- Use collections.deque for efficient sliding window management
- Use time.time() for timestamps
- Single-threaded implementation
- Compact, readable code

Return ONLY the Python class code, no explanations or markdown."""

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
    lines = response_text.strip().split('\n')
    code_lines = []
    in_code = False
    
    for line in lines:
        if line.strip().startswith('