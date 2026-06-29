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
        for neighbor in graph[task]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
    return result
if __name__ == '__main__':
    test_cases = [({'a': [], 'b': ['a'], 'c': ['b']}, ['a', 'b', 'c']), ({'a': [], 'b': [], 'c': ['a', 'b']}, ['a', 'b', 'c']), ({'a': [], 'b': [], 'c': []}, ['a', 'b', 'c']), ({'a': [], 'b': ['a'], 'c': ['a'], 'd': ['b', 'c']}, ['a', 'b', 'c', 'd'])]
    for deps, expected in test_cases:
        result = dependency_order(deps)
        print(f'Input: {deps}')
        print(f'Output: {result}')
        print()
    try:
        cycle_deps = {'a': ['b'], 'b': ['a']}
        dependency_order(cycle_deps)
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
        print(f'Correctly detected cycle: {e}')