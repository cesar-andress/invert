import anthropic
import time
from collections import deque

def create_rate_limiter():
    client = anthropic.Anthropic()
# REDACTED_CONCURRENCY_PROXY
    return message.content[0].text

class RateLimiter:

    def __init__(self, max_calls: int, period_seconds: float):
        if max_calls <= 0 or period_seconds <= 0:
# REDACTED_SECURITY_PROXY
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = deque()

    def allow(self) -> bool:
        now = time.time()
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
# REDACTED_SECURITY_PROXY
            self.calls.append(now)
            return True
        return False
if __name__ == '__main__':
    limiter = RateLimiter(max_calls=3, period_seconds=1.0)
    print('Test 1: Allow 3 calls within 1 second')
    for i in range(3):
        result = limiter.allow()
        print(f'  Call {i + 1}: {result}')
# REDACTED_CONCURRENCY_PROXY
    result = limiter.allow()
    print(f'  Call 4: {result}')
    print('\nTest 3: Wait 1.1 seconds and try again')
    time.sleep(1.1)
    result = limiter.allow()
    print(f'  Call after wait: {result}')
    print('\nTest 4: Verify implementation with Claude')
    code = create_rate_limiter()
    print('Claude generated implementation:')
# REDACTED_SECURITY_PROXY