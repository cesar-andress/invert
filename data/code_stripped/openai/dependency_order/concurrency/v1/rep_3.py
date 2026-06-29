def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    from collections import defaultdict, deque

    graph = defaultdict(list)
    in_degree = {k: 0 for k in deps}

    for task, neighbors in deps.items():
        for neighbor in neighbors:
            graph[task].append(neighbor)
            in_degree[neighbor] += 1

    queue = deque([task for task in in_degree if in_degree[task] == 0])
    order = []

    while queue:
        task = queue.popleft()
        order.append(task)
        for neighbor in graph[task]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(deps):
        raise Exception("Cycle detected in dependencies")

    return order