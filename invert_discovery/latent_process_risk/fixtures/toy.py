from __future__ import annotations

from dataclasses import dataclass

from invert_discovery.latent_process_risk.types import ProgramInput, PublicRun


@dataclass(frozen=True)
class ToyFixture:
    name: str
    program: ProgramInput
    public_pass: bool
    withheld_pass: bool
    timed_out: bool = False
    syntax_error: bool = False
    expect_deterministic: bool = True


def _run(
    test_index: int,
    repeat_index: int,
    output: str,
    wall: float = 0.01,
    opcodes: tuple[tuple[str, int], ...] = (("LOAD_FAST", 3), ("RETURN_VALUE", 1)),
) -> PublicRun:
    return PublicRun(
        test_index=test_index,
        repeat_index=repeat_index,
        output=output,
        wall_time=wall,
        cpu_time=wall * 0.9,
        peak_rss=1024,
        opcode_counts=opcodes,
    )


TOY_FIXTURES: tuple[ToyFixture, ...] = (
    ToyFixture(
        name="public_pass_hidden_pass",
        program=ProgramInput(
            "toy_ok",
            "def solve():\n    return 42\n",
            (
                _run(0, 0, "42"),
                _run(0, 1, "42"),
                _run(0, 2, "42"),
            ),
        ),
        public_pass=True,
        withheld_pass=True,
    ),
    ToyFixture(
        name="public_pass_hidden_fail",
        program=ProgramInput(
            "toy_latent",
            "def solve():\n    return 0\n",
            (
                _run(0, 0, "42", opcodes=(("LOAD_CONST", 2), ("RETURN_VALUE", 1))),
                _run(0, 1, "42", opcodes=(("LOAD_CONST", 2), ("RETURN_VALUE", 1))),
                _run(0, 2, "42", opcodes=(("LOAD_CONST", 2), ("RETURN_VALUE", 1))),
            ),
        ),
        public_pass=True,
        withheld_pass=False,
    ),
    ToyFixture(
        name="public_fail",
        program=ProgramInput("toy_fail", "def solve():\n    return 0\n", (_run(0, 0, "0"),)),
        public_pass=False,
        withheld_pass=False,
    ),
    ToyFixture(
        name="timeout",
        program=ProgramInput("toy_timeout", "while True: pass\n", ()),
        public_pass=False,
        withheld_pass=False,
        timed_out=True,
    ),
    ToyFixture(
        name="syntax_error",
        program=ProgramInput("toy_syntax", "def solve(:\n", ()),
        public_pass=False,
        withheld_pass=False,
        syntax_error=True,
    ),
    ToyFixture(
        name="deterministic_execution",
        program=ProgramInput(
            "toy_det",
            "def solve():\n    return sum(range(5))\n",
            tuple(_run(0, r, "10") for r in range(3)),
        ),
        public_pass=True,
        withheld_pass=True,
        expect_deterministic=True,
    ),
    ToyFixture(
        name="unstable_execution",
        program=ProgramInput(
            "toy_unstable",
            "def solve():\n    return 1\n",
            (
                _run(0, 0, "1", wall=0.01),
                _run(0, 1, "2", wall=0.50),
                _run(0, 2, "1", wall=0.02),
            ),
        ),
        public_pass=True,
        withheld_pass=True,
        expect_deterministic=False,
    ),
)
