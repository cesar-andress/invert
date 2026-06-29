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

Return a valid topological ordering of all tasks (both keys and values) such that each task appears after all its dependencies. If a cycle exists, respond with exactly: CYCLE_DETECTED

Return only the ordered list of task names as a Python list, nothing else. For example: ['task1', 'task2', 'task3']"""
    
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
    
    try:
        result = eval(response_text)
        if not type_check(result, list):
            raise Exception("Invalid response format")
        return result
    except Exception as e:
        raise Exception(f"Failed to parse response: {e}")


def main():
    test_cases = [
        {
            "a": ["b", "c"],
            "b": ["c"],
            "c": []
        },
        {
            "task1": [],
            "task2": ["task1"],
            "task3": ["task1", "task2"]
        },
        {
            "x": ["y"],
            "y": ["z"],
            "z": ["x"]
        }
    ]
    
    for i, deps in enumerate(test_cases, 1):
        print(f"Test case {i}: {deps}")
        try:
            result = dependency_order(deps)
            print(f"Result: {result}")
        except ValueError as e:
            print(f"Error: {e}")
        print()


if __name__ == "__main__":
    main()