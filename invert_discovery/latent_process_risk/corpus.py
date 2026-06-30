from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator


@dataclass(frozen=True)
class ProblemStub:
    problem_id: str
    source: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]


class TacoLoader:
    """Placeholder — loads BAAI/TACO when datasets package available."""

    def __init__(self, split: str = "test") -> None:
        self.split = split

    def iter_problems(self) -> Iterator[ProblemStub]:
        if False:  # pragma: no cover
            yield ProblemStub("", "", (), ())
        return
        yield  # type: ignore[misc]


class CodeContestsPlusVerifiedLoader:
    """Placeholder — loads ByteDance-Seed/Code-Contests-Plus Verified subset."""

    def __init__(self) -> None:
        pass

    def iter_problems(self) -> Iterator[ProblemStub]:
        if False:  # pragma: no cover
            yield ProblemStub("", "", (), ())
        return
        yield  # type: ignore[misc]


def load_problem_batch(loader_name: str, limit: int | None = None) -> list[ProblemStub]:
    if loader_name == "taco":
        loader: Any = TacoLoader()
    elif loader_name == "code_contests_plus_verified":
        loader = CodeContestsPlusVerifiedLoader()
    else:
        raise ValueError(f"unknown loader: {loader_name}")
    out: list[ProblemStub] = []
    for i, prob in enumerate(loader.iter_problems()):
        if limit is not None and i >= limit:
            break
        out.append(prob)
    return out
