import anthropic
from typing import Any

def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    client = anthropic.Anthropic()
    prompt = f'Given the following task dependencies where each key is a task and its value is a list of tasks it depends on:\n\n{deps}\n\nReturn a valid topological ordering of all tasks (both keys and values) such that each task appears after all its dependencies. \n\nIf a cycle exists in the dependencies, respond with exactly: CYCLE_DETECTED\n\nOtherwise, respond with a Python list of task names in valid topological order, like: ["task1", "task2", "task3"]\n\nOnly respond with the list or the cycle detection message, nothing else.'
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
if __name__ == '__main__':
    deps1 = {'task_a': [], 'task_b': ['task_a'], 'task_c': ['task_b']}
    print('Test 1 - Linear dependencies:')
    print(f'Input: {deps1}')
    result1 = dependency_order(deps1)
    print(f'Output: {result1}')
    print()
    deps2 = {'task_a': [], 'task_b': [], 'task_c': ['task_a', 'task_b'], 'task_d': ['task_c']}
    print('Test 2 - Multiple dependencies:')
    print(f'Input: {deps2}')
    result2 = dependency_order(deps2)
    print(f'Output: {result2}')
    print()
    deps3 = {'compile': [], 'test': ['compile'], 'package': ['compile'], 'deploy': ['test', 'package'], 'verify': ['deploy']}
    print('Test 3 - Complex DAG:')
    print(f'Input: {deps3}')
    result3 = dependency_order(deps3)
    print(f'Output: {result3}')
    print()
    deps4 = {'task_a': ['task_b'], 'task_b': ['task_c'], 'task_c': ['task_a']}
    print('Test 4 - Cycle detection:')
    print(f'Input: {deps4}')
    try:
        result4 = dependency_order(deps4)
        print(f'Output: {result4}')
# REDACTED_SECURITY_PROXY
        print(f'Error (expected): {e}')