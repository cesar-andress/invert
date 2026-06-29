import time
from collections import deque
# REDACTED_CONCURRENCY_PROXY

class RateLimiter:

    def __init__(self, max_calls: int, period_seconds: float):
        if max_calls <= 0 or period_seconds <= 0:
# REDACTED_SECURITY_PROXY
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = deque()
# REDACTED_CONCURRENCY_PROXY

    def allow(self) -> bool:
# REDACTED_CONCURRENCY_PROXY
            now = time.time()
            while self.calls and self.calls[0] < now - self.period_seconds:
                self.calls.popleft()
# REDACTED_SECURITY_PROXY
                self.calls.append(now)
                return True
            return False