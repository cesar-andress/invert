from __future__ import annotations

from invert_core.eager_lazy_tasks import EagerLazyTask

EAGER_LAZY_METHOD_LABELS = {
    "eager": "Eager feature pipeline",
    "lazy": "Lazy feature pipeline",
}

EAGER_LAZY_METHOD_OPERATIONAL = {
    "eager": (
        "During __init__, call feature_a_fn(x), feature_b_fn(x), and feature_c_fn(x). "
        "Store all three results. "
        "get_feature_a, get_feature_b, and get_feature_c must only return cached values. "
        "Do not recompute in getters."
    ),
    "lazy": (
        "Do not call any feature function during __init__. "
        "Each getter must call only its corresponding feature function on first request. "
        "Cache the result. "
        "Repeated calls must not recompute. "
        "Unrequested features must not be computed."
    ),
}


def build_eager_lazy_generation_prompt(
    task: EagerLazyTask, method: str, *, language: str = "python"
) -> str:
    if method not in EAGER_LAZY_METHOD_LABELS:
        raise ValueError(f"Unknown method: {method}")

    return f"""Write {language} code only.
No explanations.
No markdown.
No code fences.
One self-contained implementation.
Use only the Python standard library.
Do not include demo code or print statements.

Task ID: {task.task_id}
Input vector x: {task.x}

Feature formulas (implemented by supplied callbacks, not reimplemented inline):
- feature_a = sum(x_i ** 2 for x_i in x)
- feature_b = sum(abs(x_i) for x_i in x)
- feature_c = max(x) - min(x)

Required class (exact name and API):

class FeaturePipeline:
    def __init__(self, x, feature_a_fn, feature_b_fn, feature_c_fn):
        ...
    def get_feature_a(self):
        ...
    def get_feature_b(self):
        ...
    def get_feature_c(self):
        ...

Method label: {EAGER_LAZY_METHOD_LABELS[method]}
Operational requirement: {EAGER_LAZY_METHOD_OPERATIONAL[method]}

The generated class must call the supplied feature_a_fn, feature_b_fn, and feature_c_fn
callbacks to compute features. Do not duplicate the feature formulas without calling the callbacks.
"""


def build_eager_lazy_stub_code(task: EagerLazyTask, method: str) -> str:
    if method == "eager":
        body = (
            "    def __init__(self, x, feature_a_fn, feature_b_fn, feature_c_fn):\n"
            "        self._a = feature_a_fn(x)\n"
            "        self._b = feature_b_fn(x)\n"
            "        self._c = feature_c_fn(x)\n"
            "\n"
            "    def get_feature_a(self):\n"
            "        return self._a\n"
            "\n"
            "    def get_feature_b(self):\n"
            "        return self._b\n"
            "\n"
            "    def get_feature_c(self):\n"
            "        return self._c\n"
        )
    else:
        body = (
            "    def __init__(self, x, feature_a_fn, feature_b_fn, feature_c_fn):\n"
            "        self._x = x\n"
            "        self._feature_a_fn = feature_a_fn\n"
            "        self._feature_b_fn = feature_b_fn\n"
            "        self._feature_c_fn = feature_c_fn\n"
            "        self._a = None\n"
            "        self._b = None\n"
            "        self._c = None\n"
            "\n"
            "    def get_feature_a(self):\n"
            "        if self._a is None:\n"
            "            self._a = self._feature_a_fn(self._x)\n"
            "        return self._a\n"
            "\n"
            "    def get_feature_b(self):\n"
            "        if self._b is None:\n"
            "            self._b = self._feature_b_fn(self._x)\n"
            "        return self._b\n"
            "\n"
            "    def get_feature_c(self):\n"
            "        if self._c is None:\n"
            "            self._c = self._feature_c_fn(self._x)\n"
            "        return self._c\n"
        )
    return f"# Stub {method} for {task.task_id}\nclass FeaturePipeline:\n{body}"
