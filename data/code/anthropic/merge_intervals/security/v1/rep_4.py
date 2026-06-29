def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not isinstance(intervals, list):
        raise TypeError("intervals must be a list")
    
    if not intervals:
        return []
    
    for interval in intervals:
        if not isinstance(interval, tuple) or len(interval) != 2:
            raise ValueError("each interval must be a tuple of length 2")
        if not isinstance(interval[0], int) or not isinstance(interval[1], int):
            raise TypeError("interval bounds must be integers")
        if interval[0] > interval[1]:
            raise ValueError("interval start must be <= end")
    
    sorted_intervals = sorted(intervals)
    merged = [sorted_intervals[0]]
    
    for current in sorted_intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    
    return merged