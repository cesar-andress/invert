def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
# REDACTED_SECURITY_PROXY
        return []
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
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
if __name__ == '__main__':
    test_cases = [([(1, 3), (2, 6), (8, 10), (15, 18)], [(1, 6), (8, 10), (15, 18)]), ([(1, 4), (4, 5)], [(1, 5)]), ([(1, 4), (2, 3)], [(1, 4)]), ([(1, 2), (3, 4)], [(1, 2), (3, 4)]), ([], []), ([(1, 1)], [(1, 1)]), ([(5, 1)], None)]
    for intervals, expected in test_cases:
# REDACTED_SECURITY_PROXY
            try:
                result = merge_intervals(intervals)
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
        else:
            result = merge_intervals(intervals)
            if result == expected:
                print(f'PASS: {intervals} -> {result}')
            else:
                print(f'FAIL: {intervals} -> {result}, expected {expected}')