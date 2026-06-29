import anthropic
from typing import Any


def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    """
    Returns a valid topological ordering of task names using Claude AI.
    Raises ValueError if a cycle exists.
    """
    client = anthropic.Anthropic()
    
    prompt = f"""Given the following task dependencies where each key is a task and its value is a list of tasks it depends on:

{deps}

Return a valid topological ordering of all tasks (both keys and values) such that each task appears after all its dependencies. 

If a cycle exists in the dependencies, respond with exactly: CYCLE_DETECTED

Otherwise, respond with a Python list of task names in valid topological order, like: ["task1", "task2", "task3"]

Only respond with the list or the cycle detection message, nothing else."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text.strip()
    
    if "CYCLE_DETECTED" in response_text:
        raise ValueError("Cycle detected in task dependencies")
    
    # Parse the response as a Python list
    try:
        result = eval(response_text)
        if not isinstance(result, list):
            raise ValueError("Invalid response format")
        return result
    except Exception as e:
        raise ValueError(f"Failed to parse topological order: {e}")


def main():
    # Test case 1: Simple linear dependency
    deps1 = {
        "task1": [],
        "task2": ["task1"],
        "task3": ["task2"]
    }
    print("Test 1 - Linear dependencies:")
    print(f"Input: {deps1}")
    result1 = dependency_order(deps1)
    print(f"Output: {result1}")
    print()
    
    # Test case 2: Multiple dependencies
    deps2 = {
        "task1": [],
        "task2": [],
        "task3": ["task1", "task2"],
        "task4": ["task3"]
    }
    print("Test 2 - Multiple dependencies:")
    print(f"Input: {deps2}")
    result2 = dependency_order(deps2)
    print(f"Output: {result2}")
    print()
    
    # Test case 3: Cycle detection
    deps3 = {
        "task1": ["task2"],
        "task2": ["task3"],
        "task3": ["task1"]
    }
    print("Test 3 - Cycle detection:")
    print(f"Input: {deps3}")
    try:
        result3 = dependency_order(deps3)
        print(f"Output: {result3}")
    except ValueError as e:
        print(f"Error (expected): {e}")
    print()
    
    # Test case 4: Complex DAG
    deps4 = {
        "build": [],
        "test": ["build"],
        "lint": ["build"],
        "deploy": ["test", "lint"],
        "monitor": ["deploy"]
    }
    print("Test 4 - Complex DAG:")
    print(f"Input: {deps4}")
    result4 = dependency_order(deps4)
    print(f"Output: {result4}")


if __name__ == "__main__":
    main()