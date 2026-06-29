from __future__ import annotations

from invert.schemas import DIMENSION_NAMES, Task


def _format_dimensions(task: Task, dimension_values: dict[str, str]) -> str:
    lines = []
    for name in DIMENSION_NAMES:
        if name not in task.dimensions:
            continue
        value_key = dimension_values.get(name, "v0")
        spec = task.dimensions[name]
        text = spec.v0 if value_key == "v0" else spec.v1
        lines.append(f"- {name} ({value_key}): {text}")
    return "\n".join(lines)


def build_generation_prompt(task: Task, dimension_values: dict[str, str]) -> str:
    dims = _format_dimensions(task, dimension_values)
    return f"""Implement the following programming task in Python.

## Functional behavior
{task.functional_behavior}

## Intent dimensions
Apply ALL of the following intent constraints when writing the code:
{dims}

## Output requirements
- Return Python code only.
- Provide one self-contained implementation in a single file.
- Do not include explanations, markdown, or text outside the code.
- Do not wrap the code in markdown fences.
"""


def build_recovery_prompt(code: str, task: Task) -> str:
    dim_list = ", ".join(DIMENSION_NAMES)
    return f"""You are a blind intent recovery judge.

Given only the generated code and the functional specification below, infer whether each intent dimension was set to v0 or v1.

## Functional behavior
{task.functional_behavior}

## Generated code
{code}

## Dimensions to classify
For each dimension, output "v0" or "v1" and a confidence score from 0.0 to 1.0.

Dimensions: {dim_list}

## Output format
Return JSON only. No markdown, no explanation.

Example format:
{{
  "performance": {{"value": "v0", "confidence": 0.73}},
  "security": {{"value": "v1", "confidence": 0.81}},
  "error_handling": {{"value": "v0", "confidence": 0.62}},
  "api_preference": {{"value": "v1", "confidence": 0.77}},
  "readability": {{"value": "v0", "confidence": 0.91}},
  "maintainability": {{"value": "v1", "confidence": 0.88}},
  "edge_cases": {{"value": "v1", "confidence": 0.79}},
  "concurrency": {{"value": "v0", "confidence": 0.55}}
}}
"""
