from __future__ import annotations

import ast
import hashlib

AST_NODE_TYPES: tuple[str, ...] = (
    "Module",
    "FunctionDef",
    "AsyncFunctionDef",
    "Return",
    "Assign",
    "AugAssign",
    "If",
    "For",
    "While",
    "With",
    "Try",
    "ExceptHandler",
    "Call",
    "Name",
    "Constant",
    "BinOp",
    "Compare",
    "List",
    "Dict",
    "Tuple",
    "Subscript",
    "Attribute",
    "Import",
    "ImportFrom",
    "Pass",
)


def ast_features(source: str) -> tuple[float, ...]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return tuple(0.0 for _ in range(len(AST_NODE_TYPES) + 4))

    hist = [0.0] * len(AST_NODE_TYPES)
    for node in ast.walk(tree):
        name = type(node).__name__
        if name in AST_NODE_TYPES:
            hist[AST_NODE_TYPES.index(name)] += 1.0

    depth = _max_depth(tree)
    ast_hash = float(int(hashlib.sha256(ast.dump(tree).encode()).hexdigest()[:8], 16))
    cfg_nodes = float(sum(isinstance(n, (ast.If, ast.For, ast.While)) for n in ast.walk(tree)) + 1)
    branches = float(sum(isinstance(n, (ast.If, ast.For, ast.While, ast.ExceptHandler)) for n in ast.walk(tree)))

    return tuple(hist + [depth, ast_hash, cfg_nodes, branches])


def _max_depth(node: ast.AST, depth: int = 0) -> float:
    child_depths = [_max_depth(child, depth + 1) for child in ast.iter_child_nodes(node)]
    return float(max([depth, *child_depths]))
