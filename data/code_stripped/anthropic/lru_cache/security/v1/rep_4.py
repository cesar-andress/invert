from anthropic import Anthropic

client = Anthropic()
conversation_history = []

def chat(user_message):
    """Send a message and get a response from Claude."""
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8096,
        system="""You are a Python programming expert. When asked to implement code, 
provide only valid, working Python code without any markdown formatting, explanations, 
or text outside the code. The code should be production-ready and follow best practices.""",
        messages=conversation_history
    )
    
    assistant_message = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })
    
    return assistant_message

def main():
    """Main function to implement LRUCache through multi-turn conversation."""
    
    # First turn: Ask Claude to implement the LRUCache
    print("Turn 1: Requesting LRUCache implementation...")
    response1 = chat("""Implement a class LRUCache with methods get(key) and put(key, value) 
supporting a fixed capacity. get returns -1 for missing keys. Both operations must be O(1) 
average time. Apply these constraints:
- performance (v0): No specific complexity requirement.
- security (v1): Validate and clean all external inputs.
- error_handling (v0): Fail fast by raising exceptions on invalid input.
- api_preference (v0): Use Python standard library utilities where appropriate.
- readability (v0): Prefer compact code with short names and minimal comments.
- maintainability (v0): Implement the solution as a single function.
- edge_cases (v0): Assume inputs are well formed.
- concurrency (v0): Assume single-threaded execution.

Return only the Python code, no explanations.""")
    
    print("Claude's response:")
    print(response1)
    print("\n" + "="*50 + "\n")
    
    # Second turn: Ask for test cases
    print("Turn 2: Requesting test cases...")
    response2 = chat("""Now provide comprehensive test cases for the LRUCache implementation. 
Include tests for:
1. Basic get and put operations
2. Capacity limits and eviction
3. LRU ordering
4. Edge cases
Return only the Python test code, no explanations.""")
    
    print("Claude's response:")
    print(response2)
    print("\n" + "="*50 + "\n")
    
    # Third turn: Ask for optimization suggestions
    print("Turn 3: Requesting optimization review...")
    response3 = chat("""Review the LRUCache implementation for any potential optimizations 
or improvements while maintaining O(1) operations. Focus on:
1. Memory efficiency
2. Code clarity
3. Edge case handling
Provide only the optimized Python code, no explanations.""")
    
    print("Claude's response:")
    print(response3)
    print("\n" + "="*50 + "\n")
    
    # Extract and execute the final implementation
    print("Extracting and testing the final implementation...")
    
    # Get the implementation from the first response
    implementation_code = response1.trim()
    
    # Create a test to verify the implementation works
    test_code = """
# Test the LRUCache implementation
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
assert cache.get(1) == 1
cache.put(3, 3)
assert cache.get(2) == -1
cache.put(4, 4)
assert cache.get(1) == -1
assert cache.get(3) == 3
assert cache.get(4) == 4
print("All tests passed!")
"""
    
    try:
        # Execute the implementation and tests
        exec(implementation_code + "\n" + test_code)
    except Exception as e:
        print(f"Error executing code: {e}")
        print("Implementation code:")
        print(implementation_code)

if __name__ == "__main__":
    main()