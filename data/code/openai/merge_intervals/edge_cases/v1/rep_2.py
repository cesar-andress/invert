def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if intervals is None:
        raise ValueError("Input cannot be None")
    if not isinstance(intervals, list):
        raise TypeError("Input must be a list")
    
    intervals.sort(key=lambda x: x[0])
    merged = []
    
    for interval in intervals:
        if not isinstance(interval, tuple) or len(interval) != 2:
            raise ValueError("Each interval must be a tuple of two integers")
        if interval[0] > interval[1]:
            raise ValueError("Invalid interval: start must not be greater than end")
        
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], interval[1]))
    
    return merged