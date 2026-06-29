from __future__ import annotations

import ast
from enum import Enum


class StripLevel(str, Enum):
    RAW = "raw"
    NO_COMMENTS = "no_comments"
    RENAMED = "renamed"
    NO_IMPORTS = "no_imports"
    FORMAT_NORMALIZED = "format_normalized"


_STRIP_ORDER = [
    StripLevel.RAW,
    StripLevel.NO_COMMENTS,
    StripLevel.RENAMED,
    StripLevel.NO_IMPORTS,
    StripLevel.FORMAT_NORMALIZED,
]


def _strip_docstrings(node: ast.AST) -> None:
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if (
                child.body
                and isinstance(child.body[0], ast.Expr)
                and isinstance(child.body[0].value, ast.Constant)
                and isinstance(child.body[0].value.value, str)
            ):
                child.body = child.body[1:]
        _strip_docstrings(child)


class _CommentStripper(ast.NodeTransformer):
    pass


def _remove_comments(code: str) -> str:
    tree = ast.parse(code)
    _strip_docstrings(tree)
    return ast.unparse(tree)


class _IdentifierRenamer(ast.NodeTransformer):
    def __init__(self) -> None:
        self._mapping: dict[str, str] = {}
        self._counter = 0
        self._reserved = set(dir(__builtins__)) | {
            "self",
            "cls",
            "True",
            "False",
            "None",
        }

    def _new_name(self, old: str) -> str:
        if old in self._reserved:
            return old
        if old not in self._mapping:
            self._mapping[old] = f"x{self._counter}"
            self._counter += 1
        return self._mapping[old]

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if isinstance(node.ctx, (ast.Store, ast.Load, ast.Del)):
            node.id = self._new_name(node.id)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        node.name = self._new_name(node.name)
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        node.name = self._new_name(node.name)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        node.name = self._new_name(node.name)
        self.generic_visit(node)
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        node.arg = self._new_name(node.arg)
        return node

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.ExceptHandler:
        if node.name:
            node.name = self._new_name(node.name)
        self.generic_visit(node)
        return node


def _rename_identifiers(code: str) -> str:
    tree = ast.parse(code)
    renamer = _IdentifierRenamer()
    tree = renamer.visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


class _ImportStripper(ast.NodeTransformer):
    def visit_Import(self, node: ast.Import) -> None:
        return None

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        return None


def _remove_imports(code: str) -> str:
    tree = ast.parse(code)
    tree = _ImportStripper().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def _format_normalize(code: str) -> str:
    tree = ast.parse(code)
    return ast.unparse(tree)


def strip_code(code: str, level: StripLevel | str) -> str:
    """Apply stripping transforms cumulatively up to the requested level."""
    if isinstance(level, str):
        level = StripLevel(level)

    if level == StripLevel.RAW:
        return code

    result = code
    idx = _STRIP_ORDER.index(level)
    for step in _STRIP_ORDER[1 : idx + 1]:
        if step == StripLevel.NO_COMMENTS:
            result = _remove_comments(result)
        elif step == StripLevel.RENAMED:
            result = _rename_identifiers(result)
        elif step == StripLevel.NO_IMPORTS:
            result = _remove_imports(result)
        elif step == StripLevel.FORMAT_NORMALIZED:
            result = _format_normalize(result)
    return result


def strip_file(path: str, level: StripLevel | str) -> str:
    from pathlib import Path

    code = Path(path).read_text(encoding="utf-8")
    return strip_code(code, level)
