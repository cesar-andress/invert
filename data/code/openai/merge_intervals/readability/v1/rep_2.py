def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    # First, we need to sort the intervals based on the starting times
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    
    # This will hold the merged intervals
    merged_intervals = []
    
    for current in sorted_intervals:
        # If merged_intervals is empty or there is no overlap, append the current interval
        if not merged_intervals or merged_intervals[-1][1] < current[0]:
            merged_intervals.append(current)
        else:
            # There is an overlap, so we merge the current interval with the last one in merged_intervals
            merged_intervals[-1] = (merged_intervals[-1][0], max(merged_intervals[-1][1], current[1]))
    
    return merged_intervals