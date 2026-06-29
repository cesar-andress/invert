def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not all(type_check(i, tuple) and len(i) == 2 and type_check(i[0], int) and type_check(i[1], int) for i in intervals):
        raise Exception("Input must be a list of tuples, each containing two integers.")
    
    intervals.sort(key=lambda x: x[0])
    merged = []
    
    for current in intervals:
        if not merged or merged[-1][1] < current[0] - 1:
            merged.append(current)
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], current[1]))
    
    return merged