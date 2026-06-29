class RateLimiter:
    def __init__(self, max_calls: int, period_seconds: float):
        if not isinstance(max_calls, int) or max_calls <= 0:
            raise ValueError("max_calls must be a positive integer")
        if not isinstance(period_seconds, (int, float)) or period_seconds <= 0:
            raise ValueError("period_seconds must be a positive number")
        
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = []
    
    def allow(self) -> bool:
        from time import time
        
        current_time = time()
        self.calls = [t for t in self.calls if t > current_time - self.period_seconds]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(current_time)
            return True
        return False