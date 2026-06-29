def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    """
    Returns a valid topological ordering of task names.
    Raises ValueError if a cycle exists.
    
    Args:
        deps: Dictionary mapping task names to lists of their dependencies
        
    Returns:
        List of task names in valid dependency order
        
    Raises:
        ValueError: If a cycle is detected in the dependency graph
    """
    # Input validation
    if not isinstance(deps, dict):
        raise ValueError("Input must be a dictionary")
    
    for task, dep_list in deps.items():
        if not isinstance(task, str):
            raise ValueError("Task names must be strings")
        if not isinstance(dep_list, list):
            raise ValueError("Dependencies must be lists")
        for dep in dep_list:
            if not isinstance(dep, str):
                raise ValueError("Dependency names must be strings")
    
    # Build complete graph including all nodes
    all_tasks = set(deps.keys())
    for dep_list in deps.values():
        all_tasks.update(dep_list)
    
    # Initialize state: 0 = unvisited, 1 = visiting, 2 = visited
    state = {task: 0 for task in all_tasks}
    result = []
    
    def visit(task: str) -> None:
        """DFS visit function to detect cycles and build topological order."""
        if state[task] == 1:
            # Currently visiting this node - cycle detected
            raise ValueError(f"Cycle detected in dependencies involving task '{task}'")
        if state[task] == 2:
            # Already visited
            return
        
        # Mark as visiting
        state[task] = 1
        
        # Visit all dependencies
        if task in deps:
            for dep in deps[task]:
                visit(dep)
        
        # Mark as visited and add to result
        state[task] = 2
        result.append(task)
    
    # Visit all tasks
    for task in all_tasks:
        if state[task] == 0:
            visit(task)
    
    return result