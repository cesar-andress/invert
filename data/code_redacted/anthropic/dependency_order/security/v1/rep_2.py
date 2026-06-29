def dependency_order(deps: dict[str, list[str]]) -> list[str]:
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
    for task, task_deps in deps.items():
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
        for dep in task_deps:
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
    all_tasks = set(deps.keys())
    for task_deps in deps.values():
        all_tasks.update(task_deps)
    state = {task: 0 for task in all_tasks}
    result = []

    def visit(task: str) -> None:
        if state[task] == 1:
# REDACTED_SECURITY_PROXY
        if state[task] == 2:
            return
        state[task] = 1
        for dep in deps.get(task, []):
            visit(dep)
        state[task] = 2
        result.append(task)
    for task in all_tasks:
        if state[task] == 0:
            visit(task)
    return result