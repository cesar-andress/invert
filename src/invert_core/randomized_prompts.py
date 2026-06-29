from __future__ import annotations

from invert_core.deterministic_randomized_tasks import DeterministicRandomizedTask

DETERMINISTIC_RANDOMIZED_METHOD_LABELS = {
    "deterministic": "Deterministic item processing order",
    "randomized": "Randomized item processing order",
}

DETERMINISTIC_RANDOMIZED_METHOD_OPERATIONAL = {
    "deterministic": (
        "Implement ItemProcessor.process_all to process all items in deterministic sorted "
        "order or stable input order. Call visit_fn(item) exactly once when visiting each item. "
        "Ignore the return value of visit_fn. Return the original input items as a set or "
        "sorted list. The seed argument may be accepted but must not affect processing order. "
        "Do not print. No demo code."
    ),
    "randomized": (
        "Implement ItemProcessor.process_all to process all items in randomized order. "
        "Call visit_fn(item) exactly once when visiting each item. Ignore the return value of "
        "visit_fn. Return the original input items as a set or sorted list. If seed is None, "
        "executions may use fresh randomness. If seed is provided, the random order must be "
        "reproducible. Do not print. No demo code."
    ),
}


def build_deterministic_randomized_generation_prompt(
    task: DeterministicRandomizedTask,
    method: str,
    *,
    language: str = "python",
) -> str:
    if method not in DETERMINISTIC_RANDOMIZED_METHOD_LABELS:
        raise ValueError(f"Unknown method: {method}")

    return f"""Write {language} code only.
No explanations.
No markdown.
No code fences.
One self-contained implementation.
Use only the Python standard library.
Do not include demo code or print statements.

Task ID: {task.task_id}
Items: {task.items}

Required class (exact name and API):

class ItemProcessor:
    def __init__(self, items, visit_fn, seed=None):
        self.items = list(items)
        self.visit_fn = visit_fn
        self.seed = seed

    def process_all(self):
        ...

Method label: {DETERMINISTIC_RANDOMIZED_METHOD_LABELS[method]}
Operational requirement: {DETERMINISTIC_RANDOMIZED_METHOD_OPERATIONAL[method]}

visit_fn(item) is a side-effect callback only. Call it exactly once per item when that item
is visited. Do not accumulate or return visit_fn(item) results.
process_all() must return the original input items as a set or sorted list, independent of
visit order.
"""


def build_deterministic_randomized_stub_code(
    task: DeterministicRandomizedTask, method: str
) -> str:
    if method == "deterministic":
        body = (
            "    def __init__(self, items, visit_fn, seed=None):\n"
            "        self.items = list(items)\n"
            "        self.visit_fn = visit_fn\n"
            "        self.seed = seed\n"
            "\n"
            "    def process_all(self):\n"
            "        for item in sorted(self.items, key=str):\n"
            "            self.visit_fn(item)\n"
            "        return sorted(self.items, key=str)\n"
        )
    else:
        body = (
            "    def __init__(self, items, visit_fn, seed=None):\n"
            "        import random\n"
            "        self.items = list(items)\n"
            "        self.visit_fn = visit_fn\n"
            "        self.seed = seed\n"
            "        self._rng = random.Random(seed)\n"
            "\n"
            "    def process_all(self):\n"
            "        order = list(self.items)\n"
            "        self._rng.shuffle(order)\n"
            "        for item in order:\n"
            "            self.visit_fn(item)\n"
            "        return sorted(self.items, key=str)\n"
        )
    return f"# Stub {method} for {task.task_id}\nclass ItemProcessor:\n{body}"
