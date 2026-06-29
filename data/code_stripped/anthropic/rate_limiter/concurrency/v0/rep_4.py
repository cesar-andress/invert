import anthropic
import json
from time import time


def create_rate_limiter_implementation():
    """Use Claude to generate a RateLimiter implementation."""
    client = anthropic.Anthropic()
    
    prompt = """Implement a Python class RateLimiter with the following requirements:

1. Constructor: RateLimiter(max_calls: int, period_seconds: float)
2. Method: allow() -> bool that returns True if a call is permitted under a sliding window limit
3. The sliding window should track calls within the last period_seconds
4. Return True if the number of calls in the window is less than max_calls, False otherwise
5. Use time.time() for timestamps
6. Keep implementation compact and efficient
7. No input validation needed
8. Single-threaded execution assumed

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
    # Remove markdown code blocks if present
    if "