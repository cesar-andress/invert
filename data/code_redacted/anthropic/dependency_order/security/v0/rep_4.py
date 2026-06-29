def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    graph = {task: [] for task in deps}
    in_degree = {task: 0 for task in deps}
    for task, task_deps in deps.items():
        for dep in task_deps:
            if dep not in graph:
                graph[dep] = []
            if dep not in in_degree:
                in_degree[dep] = 0
    for task, task_deps in deps.items():
        for dep in task_deps:
            graph[dep].append(task)
            in_degree[task] += 1
    queue = [task for task in graph if in_degree[task] == 0]
    result = []
    while queue:
        queue.sort()
        task = queue.pop(0)
        result.append(task)
        for dependent in graph[task]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
    return result
if __name__ == '__main__':
    test_cases = [{'a': [], 'b': ['a'], 'c': ['b']}, {'a': [], 'b': [], 'c': ['a', 'b'], 'd': ['c']}, {'a': [], 'b': [], 'c': []}, {'task1': [], 'task2': ['task1'], 'task3': ['task1'], 'task4': ['task2', 'task3']}]
    for i, test in enumerate(test_cases):
        try:
            result = dependency_order(test)
            print(f'Test {i + 1}: {result}')
# REDACTED_SECURITY_PROXY
            print(f'Test {i + 1}: Error - {e}')
    print('\nTesting cycle detection:')
    cycle_test = {'a': ['b'], 'b': ['c'], 'c': ['a']}
    try:
        result = dependency_order(cycle_test)
        print(f'Cycle test: {result}')
# REDACTED_SECURITY_PROXY
        print(f'Cycle test: Correctly detected - {e}')