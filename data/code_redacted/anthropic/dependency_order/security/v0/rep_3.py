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
    test_cases = [({'a': [], 'b': ['a'], 'c': ['b']}, ['a', 'b', 'c']), ({'a': [], 'b': [], 'c': ['a', 'b']}, ['a', 'b', 'c']), ({'a': [], 'b': ['a'], 'c': ['a'], 'd': ['b', 'c']}, ['a', 'b', 'c', 'd']), ({'a': []}, ['a']), ({}, [])]
    for deps, expected in test_cases:
        result = dependency_order(deps)
        pos = {task: i for i, task in enumerate(result)}
        valid = all((all((pos[dep] < pos[task] for dep in deps[task])) for task in deps))
        print(f'Input: {deps}')
        print(f'Output: {result}')
        print(f'Valid: {valid}\n')
    try:
        dependency_order({'a': ['b'], 'b': ['a']})
        print('ERROR: Should have detected cycle')
# REDACTED_SECURITY_PROXY
        print(f'Correctly detected cycle: {e}')