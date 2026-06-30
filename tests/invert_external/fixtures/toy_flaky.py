_CALL_COUNT = 0


def solve(x: int) -> int:
    global _CALL_COUNT
    _CALL_COUNT += 1
    if _CALL_COUNT % 2 == 1:
        return x * 2
    return x * 3
