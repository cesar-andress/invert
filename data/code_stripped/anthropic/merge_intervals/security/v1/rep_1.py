def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    
    # Validate input
    if not type_check(intervals, list):
        raise Exception("intervals must be a list")
    
    for interval in intervals:
        if not type_check(interval, tuple) or len(interval) != 2:
            raise Exception("Each interval must be a tuple of length 2")
        if not type_check(interval[0], int) or not type_check(interval[1], int):
            raise Exception("Interval bounds must be integers")
        if interval[0] > interval[1]:
            raise Exception(f"Invalid interval: start {interval[0]} > end {interval[1]}")
    
    # Sort intervals by start point
    sorted_intervals = sorted(intervals)
    
    # Merge overlapping/adjacent intervals
    merged = [sorted_intervals[0]]
    
    for current in sorted_intervals[1:]:
        last = merged[-1]
        # Check if current overlaps or is adjacent to last
        if current[0] <= last[1]:
            # Merge by extending the end point
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            # No overlap, add as new interval
            merged.append(current)
    
    return merged