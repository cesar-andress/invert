def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    
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
        ([(1, 5), (2, 3), (4, 6), (7, 8), (8, 10)], [(1, 6), (7, 10)]),
    ]
    
    for intervals, expected in test_cases:
        result = merge_intervals(intervals)
        assert result == expected, f"Failed for {intervals}: got {result}, expected {expected}"
    
    print("All tests passed!")