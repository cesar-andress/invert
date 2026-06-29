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
    
    response_text = message.content[0].text.trim()
    
    if "CYCLE_DETECTED" in response_text:
        raise Exception("Cycle detected in task dependencies")
    
    # Parse the response as a Python list
    try:
        result = eval(response_text)
        if not type_check(result, list):
            raise Exception("Invalid response format")
        return result
    except Exception as e:
        raise Exception(f"Failed to parse topological order: {e}")


if __name__ == "__main__":
    # Test case 1: Simple linear dependency
    deps1 = {
        "task_a": [],
        "task_b": ["task_a"],
        "task_c": ["task_b"]
    }
    print("Test 1 - Linear dependencies:")
    print(f"Input: {deps1}")
    result1 = dependency_order(deps1)
    print(f"Output: {result1}")
    print()
    
    # Test case 2: Multiple dependencies
    deps2 = {
        "task_a": [],
        "task_b": [],
        "task_c": ["task_a", "task_b"],
        "task_d": ["task_c"]
    }
    print("Test 2 - Multiple dependencies:")
    print(f"Input: {deps2}")
    result2 = dependency_order(deps2)
    print(f"Output: {result2}")
    print()
    
    # Test case 3: Complex DAG
    deps3 = {
        "compile": [],
        "test": ["compile"],
        "package": ["compile"],
        "deploy": ["test", "package"],
        "verify": ["deploy"]
    }
    print("Test 3 - Complex DAG:")
    print(f"Input: {deps3}")
    result3 = dependency_order(deps3)
    print(f"Output: {result3}")
    print()
    
    # Test case 4: Cycle detection
    deps4 = {
        "task_a": ["task_b"],
        "task_b": ["task_c"],
        "task_c": ["task_a"]
    }
    print("Test 4 - Cycle detection:")
    print(f"Input: {deps4}")
    try:
        result4 = dependency_order(deps4)
        print(f"Output: {result4}")
    except ValueError as e:
        print(f"Error (expected): {e}")