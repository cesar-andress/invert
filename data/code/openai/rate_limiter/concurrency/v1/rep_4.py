import time
from collections import deque
from threading import Lock

class RateLimiter:
    def __init__(self, max_calls: int, period_seconds: float):
        if max_calls <= 0 or period_seconds <= 0:
            raise ValueError("max_calls and period_seconds must be positive.")
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = deque()
        self.lock = Lock()

    def allow(self) -> bool:
        with self.lock:
            now = time.time()
            while self.calls and self.calls[0] < now - self.period_seconds:
                self.calls.popleft()
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False