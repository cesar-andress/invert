def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    
    if not isinstance(intervals, list):
        raise TypeError("intervals must be a list")
    
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


if __name__ == "__main__":
    test_cases = [
        ([(1, 3), (2, 6), (8, 10), (15, 18)], [(1, 6), (8, 10), (15, 18)]),
        ([(1, 4), (4, 5)], [(1, 5)]),
        ([(1, 4), (2, 3)], [(1, 4)]),
        ([(1, 2), (3, 4)], [(1, 2), (3, 4)]),
        ([], []),
        ([(1, 1)], [(1, 1)]),
        ([(5, 1)], None),
    ]
    
    for intervals, expected in test_cases:
        if expected is None:
            try:
                result = merge_intervals(intervals)
                print(f"FAIL: {intervals} should raise ValueError but got {result}")
            except ValueError:
                print(f"PASS: {intervals} correctly raised ValueError")
        else:
            result = merge_intervals(intervals)
            if result == expected:
                print(f"PASS: {intervals} -> {result}")
            else:
                print(f"FAIL: {intervals} -> {result}, expected {expected}")