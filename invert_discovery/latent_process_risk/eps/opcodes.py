from __future__ import annotations

# 32 frozen category slots per EPS_SPECIFICATION.md / eps_go_no_go.json
OPCODE_CATEGORY_SLOTS: tuple[str, ...] = (
    "LOAD",
    "STORE",
    "BINARY",
    "COMPARE",
    "BRANCH",
    "CALL",
    "RETURN",
    "BUILD",
    "ATTR",
    "SUBSCR",
    "IMPORT",
    "JUMP",
    "LOOP",
    "EXCEPT",
    "YIELD",
    "ASYNC",
    "FORMAT",
    "DELETE",
    "NOP",
    "CACHE",
    "OTHER",
    "RESERVED_21",
    "RESERVED_22",
    "RESERVED_23",
    "RESERVED_24",
    "RESERVED_25",
    "RESERVED_26",
    "RESERVED_27",
    "RESERVED_28",
    "RESERVED_29",
    "RESERVED_30",
    "RESERVED_31",
)

_PREFIX_MAP: list[tuple[str, str]] = [
    ("LOAD_", "LOAD"),
    ("STORE_", "STORE"),
    ("BINARY_", "BINARY"),
    ("COMPARE_", "COMPARE"),
    ("POP_JUMP", "BRANCH"),
    ("JUMP", "JUMP"),
    ("CALL", "CALL"),
    ("RETURN", "RETURN"),
    ("BUILD_", "BUILD"),
    ("STORE_ATTR", "ATTR"),
    ("LOAD_ATTR", "ATTR"),
    ("SUBSCR", "SUBSCR"),
    ("IMPORT", "IMPORT"),
    ("FOR_", "LOOP"),
    ("GET_", "LOOP"),
    ("SETUP_", "EXCEPT"),
    ("RAISE", "EXCEPT"),
    ("YIELD", "YIELD"),
    ("ASYNC", "ASYNC"),
    ("FORMAT", "FORMAT"),
    ("DELETE", "DELETE"),
    ("NOP", "NOP"),
    ("CACHE", "CACHE"),
]


def opcode_to_category(opname: str) -> str:
    for prefix, cat in _PREFIX_MAP:
        if opname.startswith(prefix) or opname == prefix.rstrip("_"):
            return cat
    return "OTHER"


def category_index(category: str) -> int:
    try:
        return OPCODE_CATEGORY_SLOTS.index(category)
    except ValueError:
        return OPCODE_CATEGORY_SLOTS.index("OTHER")
