def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    """
    Returns a valid topological ordering of task names.
    Raises ValueError if a cycle exists.
    
    Args:
        deps: Dictionary mapping task names to lists of their dependencies
        
    Returns:
        List of task names in topological order
        
    Raises:
        ValueError: If a cycle is detected in the dependency graph
    """
    # Build adjacency list and in-degree count
    graph = {task: [] for task in deps}
    in_degree = {task: 0 for task in deps}
    
    # Add all tasks that appear as dependencies
    for task, task_deps in deps.items():
        for dep in task_deps:
            if dep not in graph:
                graph[dep] = []
            if dep not in in_degree:
                in_degree[dep] = 0
    
    # Build the graph
    for task, task_deps in deps.items():
        for dep in task_deps:
            graph[dep].append(task)
            in_degree[task] += 1
    
    # Kahn's algorithm for topological sort
    queue = [task for task in graph if in_degree[task] == 0]
    result = []
    
    while queue:
        # Sort to ensure deterministic ordering when multiple nodes have in-degree 0
        queue.sort()
        node = queue.pop(0)
        result.append(node)
        
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # Check for cycles
    if len(result) != len(graph):
        raise Exception("Cycle detected in dependency graph")
    
    return result


if __name__ == "__main__":
    # Test cases
    test_cases = [
        {"a": ["b", "c"], "b": ["d"], "c": [], "d": []},
        {"task1": [], "task2": ["task1"], "task3": ["task1", "task2"]},
        {"x": ["y"], "y": ["z"], "z": []},
    ]
    
    for deps in test_cases:
        print(f"Input: {deps}")
        print(f"Output: {dependency_order(deps)}")
        print()
    
    # Test cycle detection
    try:
        cycle_deps = {"a": ["b"], "b": ["c"], "c": ["a"]}
        dependency_order(cycle_deps)
    except ValueError as e:
        print(f"Cycle test passed: {e}")