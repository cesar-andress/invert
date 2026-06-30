import time

_CALL_COUNT = 0


def solve(x: int) -> int:
    global _CALL_COUNT
    _CALL_COUNT += 1
    if _CALL_COUNT > 1:
        time.sleep(1.0)
    return x * 2
