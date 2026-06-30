from __future__ import annotations

import dis

from invert_discovery.latent_process_risk.eps.opcodes import OPCODE_CATEGORY_SLOTS, category_index, opcode_to_category

STATIC_SLOTS = 32


def static_bytecode_features(source: str) -> tuple[float, ...]:
    try:
        code = compile(source, "<lpr>", "exec")
    except SyntaxError:
        return tuple(0.0 for _ in range(STATIC_SLOTS + 2))

    counts = [0.0] * STATIC_SLOTS
    branch = 0
    total = 0
    for instr in dis.get_instructions(code):
        total += 1
        cat = opcode_to_category(instr.opname)
        counts[category_index(cat)] += 1.0
        if "JUMP" in instr.opname:
            branch += 1
    total_f = float(total or 1)
    pmf = [c / total_f for c in counts]
    return tuple(pmf + [total_f, float(branch)])
