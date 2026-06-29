from anthropic import Anthropic

def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Merges overlapping or adjacent intervals and returns sorted non-overlapping intervals.
    
    Uses Claude to help verify the implementation through multi-turn conversation.
    """
    client = Anthropic()
    conversation_history = []
    
    # Initial request to Claude for implementation help
    initial_prompt = """I need to implement a function that merges overlapping or adjacent intervals.
    
The function signature is:
def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]

Requirements:
- Merge overlapping or adjacent intervals
- Return sorted non-overlapping intervals
- Handle edge cases like empty input, single interval, etc.

Can you help me think through the algorithm?"""
    
    conversation_history.append({
        "role": "user",
        "content": initial_prompt
    })
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=conversation_history
    )
    
    assistant_message = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })
    
    # Follow-up to get the actual implementation
    follow_up = """Based on your explanation, here's my implementation approach:
1. Handle empty input
2. Sort intervals by start position
3. Iterate through sorted intervals and merge overlapping ones
4. Return the merged intervals

Can you verify this approach is correct and suggest any optimizations?"""
    
    conversation_history.append({
        "role": "user",
        "content": follow_up
    })
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=conversation_history
    )
    
    conversation_history.append({
        "role": "assistant",
        "content": response.content[0].text
    })
    
    # Now implement the actual algorithm
    if not intervals:
        return []
    
    # Sort intervals by start position, then by end position
    sorted_intervals = sorted(intervals)
    
    # Merge overlapping intervals
    merged = [sorted_intervals[0]]
    
    for current_start, current_end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]
        
        # Check if current interval overlaps or is adjacent to the last merged interval
        if current_start <= last_end:
            # Merge by extending the end of the last interval
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            # No overlap, add as new interval
            merged.append((current_start, current_end))
    
    return merged


# Test the implementation
if __name__ == "__main__":
    # Test cases
    test_cases = [
        ([(1, 3), (2, 6), (8, 10), (15, 18)], [(1, 6), (8, 10), (15, 18)]),
        ([(1, 4), (4, 5)], [(1, 5)]),
        ([(1, 4), (2, 3)], [(1, 4)]),
        ([], []),
        ([(1, 1)], [(1, 1)]),
        ([(1, 5), (2, 3)], [(1, 5)]),
        ([(1, 2), (3, 4), (5, 6)], [(1, 2), (3, 4), (5, 6)]),
    ]
    
    for intervals, expected in test_cases:
        result = merge_intervals(intervals)
        status = "✓" if result == expected else "✗"
        print(f"{status} merge_intervals({intervals}) = {result}")
        if result != expected:
            print(f"  Expected: {expected}")