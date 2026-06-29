class RateLimiter:
    def __init__(self, max_calls: int, period_seconds: float):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = []
    
    def allow(self) -> bool:
        from time import time
        now = time()
        self.calls = [call for call in self.calls if now - call < self.period_seconds]
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False