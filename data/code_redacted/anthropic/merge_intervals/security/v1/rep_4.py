def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
        return []
    for interval in intervals:
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
        if interval[0] > interval[1]:
# REDACTED_SECURITY_PROXY
    sorted_intervals = sorted(intervals)
    merged = [sorted_intervals[0]]
    for current in sorted_intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    return merged