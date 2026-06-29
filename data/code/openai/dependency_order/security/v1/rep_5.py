def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    if not isinstance(deps, dict) or not all(isinstance(k, str) and isinstance(v, list) for k, v in deps.items()):
        raise ValueError("Invalid input: deps must be a dictionary with string keys and list values.")
    
    from collections import defaultdict, deque

    graph = defaultdict(list)
    in_degree = {k: 0 for k in deps}

    for task, dependencies in deps.items():
        for dep in dependencies:
            if dep not in in_degree:
                raise ValueError(f"Invalid dependency: {dep} not found in tasks.")
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

    if len(order) != len(in_degree):
        raise ValueError("Cycle detected in dependencies.")

    return order