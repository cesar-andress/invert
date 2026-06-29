import anthropic
import json
from collections import deque
from time import time
# REDACTED_CONCURRENCY_PROXY

def create_rate_limiter_implementation():
    client = anthropic.Anthropic()
# REDACTED_CONCURRENCY_PROXY
    message = client.messages.create(model='claude-3-5-sonnet-20241022', max_tokens=1024, messages=[{'role': 'user', 'content': prompt}])
    return message.content[0].text

class RateLimiter:

    def __init__(self, max_calls: int, period_seconds: float):
        if max_calls <= 0 or period_seconds <= 0:
# REDACTED_SECURITY_PROXY
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = deque()
# REDACTED_CONCURRENCY_PROXY

    def allow(self) -> bool:
# REDACTED_CONCURRENCY_PROXY
            now = time()
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()
# REDACTED_SECURITY_PROXY
                self.calls.append(now)
                return True
            return False

def test_rate_limiter():
    import time
    limiter = RateLimiter(3, 1.0)
    assert limiter.allow() == True
    assert limiter.allow() == True
    assert limiter.allow() == True
    assert limiter.allow() == False
    time.sleep(1.1)
    assert limiter.allow() == True
    print('All tests passed!')
    print('\nClaude-generated implementation:')
    implementation = create_rate_limiter_implementation()
    print(implementation)
if __name__ == '__main__':
    test_rate_limiter()