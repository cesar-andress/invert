from __future__ import annotations

import ast
import re
import tokenize
from io import BytesIO


def size_features(source: str) -> tuple[float, ...]:
    lines = source.splitlines()
    comment_lines = sum(1 for ln in lines if re.match(r"^\s*#", ln))
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return (
            float(len(source)),
            float(len(lines)),
            0.0,
            float(comment_lines),
            0.0,
            0.0,
            0.0,
        )
    funcs = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
    imports = sum(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree))
    return (
        float(len(source)),
        float(len(lines)),
        float(len(tokenize_quick(source))),
        float(comment_lines),
        float(_cyclomatic(tree)),
        float(funcs),
        float(imports),
    )


def re_comment(line: str) -> bool:
    return bool(re.match(r"^\s*#", line))


def tokenize_quick(source: str) -> list[str]:
    try:
        return [tok.string for tok in tokenize.tokenize(BytesIO(source.encode()).readline) if tok.type == 1]
    except tokenize.TokenError:
        return []


def _cyclomatic(tree: ast.AST) -> int:
    branches = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
            branches += 1
        elif isinstance(node, ast.BoolOp):
            branches += len(node.values) - 1
    return branches + 1
