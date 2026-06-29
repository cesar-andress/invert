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
        raise ValueError("deps must be a dictionary")
    
    for task, task_deps in deps.items():
        if not isinstance(task, str):
            raise ValueError("Task names must be strings")
        if not isinstance(task_deps, list):
            raise ValueError("Dependencies must be lists")
        for dep in task_deps:
            if not isinstance(dep, str):
                raise ValueError("Dependency names must be strings")
    
    # Build complete graph including all nodes
    all_tasks = set(deps.keys())
    for task_deps in deps.values():
        all_tasks.update(task_deps)
    
    # Initialize state: 0 = unvisited, 1 = visiting, 2 = visited
    state = {task: 0 for task in all_tasks}
    result = []
    
    def visit(task: str) -> None:
        """DFS visit with cycle detection"""
        if state[task] == 1:
            raise ValueError(f"Cycle detected involving task '{task}'")
        if state[task] == 2:
            return
        
        state[task] = 1
        
        # Visit dependencies
        for dep in deps.get(task, []):
            visit(dep)
        
        state[task] = 2
        result.append(task)
    
    # Visit all tasks
    for task in all_tasks:
        if state[task] == 0:
            visit(task)
    
    return result