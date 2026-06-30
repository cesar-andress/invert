"""HumanEval+ harness for output-stability pilot (no INVERT APIs)."""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
from evalplus.eval import PASS, untrusted_check
from evalplus.gen.util import trusted_exec

from invert_external.detectors.output_stability import InputBundle


def oracle_for_task(problem: dict[str, Any]) -> dict[str, Any]:
    code = problem["prompt"] + problem["canonical_solution"]
    entry = problem["entry_point"]
    base_out, base_time = trusted_exec(
        code, problem["base_input"], entry, record_time=True
    )
    plus_out, plus_time = trusted_exec(
        code, problem["plus_input"], entry, record_time=True
    )
    return {
        "base": base_out,
        "base_time": base_time,
        "plus": plus_out,
        "plus_time": plus_time,
    }


def outputs_match(output: Any, expected: Any, atol: float) -> bool:
    if output == expected:
        return True
    try:
        use_atol = atol if atol != 0 else (1e-6 if isinstance(expected, float) else 0)
        if use_atol:
            np.testing.assert_allclose(output, expected, rtol=1e-7, atol=use_atol)
            return True
    except Exception:
        return False
    return False


def evalplus_functionally_valid(
    problem: dict[str, Any], code: str, oracle: dict[str, Any]
) -> tuple[bool, str]:
    status, _ = untrusted_check(
        "humaneval",
        code,
        problem["plus_input"],
        problem["entry_point"],
        oracle["plus"],
        problem["atol"],
        oracle["plus_time"],
        fast_check=True,
    )
    if status == PASS:
        return True, ""
    return False, status


def bundle_and_validator(
    problem: dict[str, Any], oracle: dict[str, Any]
) -> tuple[InputBundle, Callable[[Any], bool]]:
    inp = problem["base_input"][0]
    expected = oracle["base"][0]
    atol = float(problem["atol"])

    def validator(output: Any) -> bool:
        return outputs_match(output, expected, atol)

    return (
        InputBundle(bundle_id="base_input_0", args=tuple(inp)),
        validator,
    )


def full_code(prompt: str, completion: str) -> str:
    from invert.generate import extract_code

    body = extract_code(completion).strip()
    if body.startswith("def "):
        return body
    return prompt + body
