def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not all(isinstance(i, tuple) and len(i) == 2 and isinstance(i[0], int) and isinstance(i[1], int) for i in intervals):
        raise ValueError("Input must be a list of tuples, each containing two integers.")
    
    intervals.sort(key=lambda x: x[0])
    merged = []
    
    for current in intervals:
        if not merged or merged[-1][1] < current[0]:
            merged.append(current)
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], current[1]))
    
    return merged