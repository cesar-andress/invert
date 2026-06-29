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
    
    # Build the graph and calculate in-degrees
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
        task = queue.pop(0)
        result.append(task)
        
        for neighbor in graph[task]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # Check if all tasks were processed (no cycle)
    if len(result) != len(graph):
        raise ValueError("Cycle detected in dependency graph")
    
    return result


if __name__ == "__main__":
    # Test cases
    test_cases = [
        # Simple linear dependency
        ({"a": [], "b": ["a"], "c": ["b"]}, ["a", "b", "c"]),
        # Multiple dependencies
        ({"a": [], "b": [], "c": ["a", "b"]}, ["a", "b", "c"]),
        # No dependencies
        ({"a": [], "b": [], "c": []}, ["a", "b", "c"]),
        # Complex graph
        ({"a": [], "b": ["a"], "c": ["a"], "d": ["b", "c"]}, ["a", "b", "c", "d"]),
    ]
    
    for deps, expected in test_cases:
        result = dependency_order(deps)
        print(f"Input: {deps}")
        print(f"Output: {result}")
        print()
    
    # Test cycle detection
    try:
        cycle_deps = {"a": ["b"], "b": ["a"]}
        dependency_order(cycle_deps)
        print("ERROR: Should have raised ValueError for cycle")
    except ValueError as e:
        print(f"Correctly detected cycle: {e}")