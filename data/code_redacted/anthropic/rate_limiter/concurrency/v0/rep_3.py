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
        while self.calls and self.calls[0] < now - self.period_seconds:
            self.calls.popleft()
# REDACTED_SECURITY_PROXY
            self.calls.append(now)
            return True
        return False

def test_rate_limiter():
    limiter = RateLimiter(3, 1.0)
    assert limiter.allow() == True
    assert limiter.allow() == True
    assert limiter.allow() == True
    assert limiter.allow() == False
    time.sleep(1.1)
    assert limiter.allow() == True
    limiter2 = RateLimiter(2, 0.1)
    assert limiter2.allow() == True
    assert limiter2.allow() == True
    assert limiter2.allow() == False
    time.sleep(0.11)
    assert limiter2.allow() == True
    limiter3 = RateLimiter(1, 0.5)
    assert limiter3.allow() == True
    assert limiter3.allow() == False
    time.sleep(0.51)
    assert limiter3.allow() == True
    print('All tests passed!')
if __name__ == '__main__':
    test_rate_limiter()