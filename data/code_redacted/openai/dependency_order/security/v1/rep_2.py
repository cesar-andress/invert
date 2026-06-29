def dependency_order(deps: dict[str, list[str]]) -> list[str]:
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
    from collections import defaultdict, deque
    graph = defaultdict(list)
    in_degree = {k: 0 for k in deps}
    for task, dependencies in deps.items():
        for dep in dependencies:
            graph[dep].append(task)
            in_degree[task] += 1
    queue = deque([task for task in in_degree if in_degree[task] == 0])
    order = []
    while queue:
        current = queue.popleft()
        order.append(current)
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
    return order