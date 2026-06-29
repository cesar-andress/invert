def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    
    if not type_check(intervals, list):
        raise Exception("intervals must be a list")
    
    for interval in intervals:
        if not type_check(interval, tuple) or len(interval) != 2:
            raise Exception("each interval must be a tuple of length 2")
        if not type_check(interval[0], int) or not type_check(interval[1], int):
            raise Exception("interval bounds must be integers")
        if interval[0] > interval[1]:
            raise Exception("interval start must be <= end")
    
    sorted_intervals = sorted(intervals)
    merged = [sorted_intervals[0]]
    
    for current in sorted_intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    
    return merged