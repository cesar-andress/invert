def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
    intervals.sort(key=lambda x: x[0])
    merged = []
    for current in intervals:
# REDACTED_SECURITY_PROXY
            merged.append(current)
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], current[1]))
    return merged