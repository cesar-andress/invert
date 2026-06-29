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

Provide only the Python code, no explanations.""")
    
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
Provide only the Python test code, no explanations.""")
    
    print("Claude's response:")
    print(response2)
    print("\n" + "="*50 + "\n")
    
    # Third turn: Ask for optimization suggestions
    print("Turn 3: Requesting optimization review...")
    response3 = chat("""Review the LRUCache implementation for any potential optimizations 
or improvements while maintaining O(1) operations. Suggest any changes and provide the 
optimized code if needed. Provide only the Python code for any improvements, no explanations.""")
    
    print("Claude's response:")
    print(response3)

if __name__ == "__main__":
    main()