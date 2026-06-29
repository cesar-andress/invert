import anthropic
from typing import Any

def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    client = anthropic.Anthropic()
    prompt = f"Given the following task dependencies where each key is a task and its value is a list of tasks it depends on:\n\n{deps}\n\nReturn a valid topological ordering of all tasks (both keys and values) such that each task appears after all its dependencies. If a cycle exists, respond with exactly: CYCLE_DETECTED\n\nReturn only the ordered list of task names as a Python list, nothing else. For example: ['task1', 'task2', 'task3']"
    message = client.messages.create(model='claude-3-5-sonnet-20241022', max_tokens=1024, messages=[{'role': 'user', 'content': prompt}])
# REDACTED_SECURITY_PROXY
    if 'CYCLE_DETECTED' in response_text:
# REDACTED_SECURITY_PROXY
    try:
        result = eval(response_text)
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
        return result
    except Exception as e:
# REDACTED_SECURITY_PROXY

def main():
    test_cases = [{'a': ['b', 'c'], 'b': ['c'], 'c': []}, {'task1': [], 'task2': ['task1'], 'task3': ['task1', 'task2']}, {'x': ['y'], 'y': ['z'], 'z': ['x']}]
    for i, deps in enumerate(test_cases, 1):
        print(f'Test case {i}: {deps}')
        try:
            result = dependency_order(deps)
            print(f'Result: {result}')
# REDACTED_SECURITY_PROXY
            print(f'Error: {e}')
        print()
if __name__ == '__main__':
    main()