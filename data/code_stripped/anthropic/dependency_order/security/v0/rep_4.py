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
        
        for dependent in graph[task]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)
    
    # Check for cycles
    if len(result) != len(graph):
        raise Exception("Cycle detected in dependency graph")
    
    return result


if __name__ == "__main__":
    # Test cases
    test_cases = [
        # Simple linear dependency
        {"a": [], "b": ["a"], "c": ["b"]},
        # Multiple dependencies
        {"a": [], "b": [], "c": ["a", "b"], "d": ["c"]},
        # No dependencies
        {"a": [], "b": [], "c": []},
        # Complex graph
        {"task1": [], "task2": ["task1"], "task3": ["task1"], "task4": ["task2", "task3"]},
    ]
    
    for i, test in enumerate(test_cases):
        try:
            result = dependency_order(test)
            print(f"Test {i+1}: {result}")
        except ValueError as e:
            print(f"Test {i+1}: Error - {e}")
    
    # Test cycle detection
    print("\nTesting cycle detection:")
    cycle_test = {"a": ["b"], "b": ["c"], "c": ["a"]}
    try:
        result = dependency_order(cycle_test)
        print(f"Cycle test: {result}")
    except ValueError as e:
        print(f"Cycle test: Correctly detected - {e}")