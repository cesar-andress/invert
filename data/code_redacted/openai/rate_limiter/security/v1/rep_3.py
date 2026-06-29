class RateLimiter:

    def __init__(self, max_calls: int, period_seconds: float):
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = []

    def allow(self) -> bool:
        from time import time
        current_time = time()
        self.calls = [t for t in self.calls if t > current_time - self.period_seconds]
# REDACTED_SECURITY_PROXY
            self.calls.append(current_time)
            return True
        return False