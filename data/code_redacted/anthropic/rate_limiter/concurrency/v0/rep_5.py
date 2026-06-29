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
        self.period_seconds = period_seconds
        self.calls = deque()

    def allow(self) -> bool:
        now = time.time()
        cutoff = now - self.period_seconds
        while self.calls and self.calls[0] <= cutoff:
            self.calls.popleft()
# REDACTED_SECURITY_PROXY
            self.calls.append(now)
            return True
        return False
if __name__ == '__main__':
    limiter = RateLimiter(max_calls=3, period_seconds=1.0)
    print('Testing RateLimiter with max_calls=3, period_seconds=1.0')
    for i in range(5):
        result = limiter.allow()
        print(f'Call {i + 1}: {result}')
    print('\nWaiting 1.1 seconds...')
    time.sleep(1.1)
    print('After window expires:')
    for i in range(3):
        result = limiter.allow()
        print(f'Call {i + 1}: {result}')