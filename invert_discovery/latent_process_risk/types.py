from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LabelStatus(str, Enum):
    PUBLIC_PASS_HIDDEN_PASS = "public_pass_hidden_pass"
    PUBLIC_PASS_HIDDEN_FAIL = "public_pass_hidden_fail"
    OUTRIGHT_FAIL = "outright_fail"
    TIMEOUT = "timeout"
    SYNTAX_ERROR = "syntax_error"
    EXECUTION_ERROR = "execution_error"
    INVALID = "invalid"


@dataclass(frozen=True)
class PublicRun:
    """Single execution on a public test — no withheld information."""

    test_index: int
    repeat_index: int
    output: str
    wall_time: float
    cpu_time: float
    peak_rss: int
    opcode_counts: tuple[tuple[str, int], ...] = ()


@dataclass(frozen=True)
class ProgramInput:
    """Extractor input — deliberately excludes labels and withheld tests."""

    program_id: str
    source: str
    public_runs: tuple[PublicRun, ...]


@dataclass(frozen=True)
class LabelRecord:
    public_pass: bool
    withheld_pass: bool
    status: LabelStatus

    @property
    def latent_incorrect(self) -> bool:
        return self.public_pass and not self.withheld_pass


FORBIDDEN_EXTRACTOR_KEYS = frozenset(
    {
        "withheld_pass",
        "withheld_fail",
        "hidden_pass",
        "hidden_fail",
        "label",
        "y",
        "latent_incorrect",
        "withheld_outputs",
        "withheld_tests",
    }
)


def reject_label_kwargs(kwargs: dict[str, Any]) -> None:
    bad = FORBIDDEN_EXTRACTOR_KEYS.intersection(kwargs)
    if bad:
        raise ValueError(f"Label leakage: forbidden kwargs {sorted(bad)}")
