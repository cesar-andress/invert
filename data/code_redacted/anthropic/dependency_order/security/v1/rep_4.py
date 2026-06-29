def dependency_order(deps: dict[str, list[str]]) -> list[str]:
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
    for task, dep_list in deps.items():
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
        for dep in dep_list:
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
    all_tasks = set(deps.keys())
    for dep_list in deps.values():
        all_tasks.update(dep_list)
    state = {task: 0 for task in all_tasks}
    result = []

    def visit(task: str) -> None:
        if state[task] == 1:
# REDACTED_SECURITY_PROXY
        if state[task] == 2:
            return
        state[task] = 1
        if task in deps:
            for dep in deps[task]:
                visit(dep)
        state[task] = 2
        result.append(task)
    for task in all_tasks:
        if state[task] == 0:
            visit(task)
    return result