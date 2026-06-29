from __future__ import annotations

import ast
import builtins
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

LOCK_MARKER_PLACEHOLDER = "# LOCK_MARKER_STRIPPED"
_SENTINEL_CALL = "__LOCK_MARKER_STRIPPED__"

_LOCK_MODULE_NAMES = frozenset({"threading", "asyncio", "concurrent", "multiprocessing"})
_LOCK_TYPE_NAMES = frozenset({"Lock", "RLock", "Semaphore"})
_LOCK_TEXT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("threading", re.compile(r"\bthreading\b", re.IGNORECASE)),
    ("asyncio", re.compile(r"\basyncio\b", re.IGNORECASE)),
    ("concurrent", re.compile(r"\bconcurrent\b", re.IGNORECASE)),
    ("multiprocessing", re.compile(r"\bmultiprocessing\b", re.IGNORECASE)),
    ("Lock", re.compile(r"\bLock\b")),
    ("RLock", re.compile(r"\bRLock\b")),
    ("Semaphore", re.compile(r"\bSemaphore\b")),
    ("mutex", re.compile(r"\bmutex\b", re.IGNORECASE)),
    ("synchronized", re.compile(r"\bsynchronized\b", re.IGNORECASE)),
    ("threadsafe", re.compile(r"\bthreadsafe\b", re.IGNORECASE)),
    ("thread_safe", re.compile(r"\bthread_safe\b", re.IGNORECASE)),
    ("thread-safe", re.compile(r"\bthread-safe\b", re.IGNORECASE)),
    ("atomic", re.compile(r"\batomic\b", re.IGNORECASE)),
    ("with_self.lock", re.compile(r"\bwith\s+self\.lock\b", re.IGNORECASE)),
    ("with_lock", re.compile(r"\bwith\s+lock\b", re.IGNORECASE)),
    (".acquire(", re.compile(r"\.acquire\s*\(")),
    (".release(", re.compile(r"\.release\s*\(")),
]


class StripLevel(str, Enum):
    RAW = "raw"
    NO_COMMENTS = "no_comments"
    RENAMED = "renamed"
    NO_IMPORTS = "no_imports"
    FORMAT_NORMALIZED = "format_normalized"
    LOCK_MARKER_STRIP = "lock_marker_strip"


_STRIP_ORDER = [
    StripLevel.RAW,
    StripLevel.NO_COMMENTS,
    StripLevel.RENAMED,
    StripLevel.NO_IMPORTS,
    StripLevel.FORMAT_NORMALIZED,
]

STANDARD_STRIP_LEVELS = list(_STRIP_ORDER)

_BUILTIN_NAMES = frozenset(dir(builtins))

PUBLIC_API_PRESERVE: dict[str, dict[str, list[str]]] = {
    "bfs_vs_dfs": {
        "classes": ["GraphTraversal"],
        "methods": ["reachable_nodes"],
        "constructor_args": ["graph", "start", "visit_fn"],
    },
    "eager_vs_lazy": {
        "classes": ["FeaturePipeline"],
        "methods": ["get_feature_a", "get_feature_b", "get_feature_c"],
        "constructor_args": ["x", "feature_a_fn", "feature_b_fn", "feature_c_fn"],
    },
    "deterministic_vs_randomized": {
        "classes": ["ItemProcessor"],
        "methods": ["process_all"],
        "constructor_args": ["items", "visit_fn", "seed"],
    },
}


def preserve_names_for_dimension(dimension: str | None) -> frozenset[str]:
    if not dimension or dimension not in PUBLIC_API_PRESERVE:
        return frozenset()
    spec = PUBLIC_API_PRESERVE[dimension]
    names: set[str] = set()
    for key in ("classes", "methods", "constructor_args"):
        names.update(spec.get(key, []))
    return frozenset(names)


def is_dynamic_dimension(dimension: str | None) -> bool:
    return dimension in PUBLIC_API_PRESERVE


@dataclass
class StripEvidence:
    markers_removed: list[str] = field(default_factory=list)
    lines_removed: int = 0
    replacements_made: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "markers_removed": self.markers_removed,
            "lines_removed": self.lines_removed,
            "replacements_made": self.replacements_made,
        }


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
    def __init__(self, *, preserve_names: frozenset[str] = frozenset()) -> None:
        self._mapping: dict[str, str] = {}
        self._counter = 0
        self._preserve_names = preserve_names
        self._reserved = set(_BUILTIN_NAMES) | {
            "self",
            "cls",
        }

    def _new_name(self, old: str) -> str:
        if old in self._reserved or old in self._preserve_names:
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
        if not (node.name.startswith("__") and node.name.endswith("__")):
            node.name = self._new_name(node.name)
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        if not (node.name.startswith("__") and node.name.endswith("__")):
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


def _import_bound_names(tree: ast.AST) -> frozenset[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    names.add(alias.asname or alias.name)
    return frozenset(names)


def _rename_identifiers(code: str, *, preserve_names: frozenset[str] | None = None) -> str:
    tree = ast.parse(code)
    preserve = (preserve_names or frozenset()) | _import_bound_names(tree)
    renamer = _IdentifierRenamer(preserve_names=preserve)
    tree = renamer.visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def _import_assignment(module: str, name: str, *, bound: str) -> ast.Assign:
    import_call = ast.Call(
        func=ast.Name(id="__import__", ctx=ast.Load()),
        args=[ast.Constant(module)],
        keywords=[
            ast.keyword(
                arg="fromlist",
                value=ast.List(elts=[ast.Constant(name)], ctx=ast.Load()),
            )
        ],
    )
    value: ast.expr = ast.Attribute(value=import_call, attr=name, ctx=ast.Load())
    return ast.Assign(
        targets=[ast.Name(id=bound, ctx=ast.Store())],
        value=value,
    )


def _materialize_imports(code: str) -> str:
    class _ImportMaterializer(ast.NodeTransformer):
        def visit_Import(self, node: ast.Import) -> list[ast.stmt]:
            out: list[ast.stmt] = []
            for alias in node.names:
                bound = alias.asname or alias.name.split(".")[0]
                out.append(
                    ast.Assign(
                        targets=[ast.Name(id=bound, ctx=ast.Store())],
                        value=ast.Call(
                            func=ast.Name(id="__import__", ctx=ast.Load()),
                            args=[ast.Constant(alias.name)],
                            keywords=[],
                        ),
                    )
                )
            return out

        def visit_ImportFrom(self, node: ast.ImportFrom) -> list[ast.stmt] | ast.AST:
            if node.module is None or node.level > 0:
                return node
            out: list[ast.stmt] = []
            for alias in node.names:
                if alias.name == "*":
                    continue
                bound = alias.asname or alias.name
                out.append(_import_assignment(node.module, alias.name, bound=bound))
            return out or node

    tree = ast.parse(code)
    tree = _ImportMaterializer().visit(tree)
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


def _call_lock_type_name(node: ast.expr) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if isinstance(func, ast.Attribute):
        if func.attr in _LOCK_TYPE_NAMES:
            return func.attr
        if isinstance(func.value, ast.Name) and func.value.id in _LOCK_MODULE_NAMES:
            return func.attr
    if isinstance(func, ast.Name) and func.id in _LOCK_TYPE_NAMES:
        return func.id
    return None


def _is_lock_factory_call(node: ast.expr) -> bool:
    return _call_lock_type_name(node) is not None


def _is_acquire_or_release_call(node: ast.expr) -> bool:
    if not isinstance(node, ast.Call):
        return False
    if isinstance(node.func, ast.Attribute):
        return node.func.attr in {"acquire", "release"}
    return False


def _placeholder_stmt() -> ast.stmt:
    return ast.Expr(
        value=ast.Call(
            func=ast.Name(id=_SENTINEL_CALL, ctx=ast.Load()),
            args=[],
            keywords=[],
        )
    )


class _LockMarkerStripper(ast.NodeTransformer):
    def __init__(self, evidence: StripEvidence) -> None:
        self.evidence = evidence
        self.lock_vars: set[str] = set()

    def _record(self, marker: str) -> None:
        if marker not in self.evidence.markers_removed:
            self.evidence.markers_removed.append(marker)

    def _module_root(self, name: str | None) -> str | None:
        if not name:
            return None
        return name.split(".")[0]

    def visit_Import(self, node: ast.Import) -> ast.stmt | None:
        for alias in node.names:
            root = self._module_root(alias.name)
            if root in _LOCK_MODULE_NAMES:
                self._record(f"import:{root}")
                self.evidence.lines_removed += 1
                return _placeholder_stmt()
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.stmt | None:
        root = self._module_root(node.module)
        if root in _LOCK_MODULE_NAMES:
            self._record(f"import_from:{root}")
            self.evidence.lines_removed += 1
            return _placeholder_stmt()
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.stmt | None:
        if _is_lock_factory_call(node.value):
            lock_type = _call_lock_type_name(node.value) or "Lock"
            self._record(f"lock_assignment:{lock_type}")
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.lock_vars.add(target.id)
            self.evidence.replacements_made += 1
            return _placeholder_stmt()
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.stmt | None:
        if node.value and _is_lock_factory_call(node.value):
            lock_type = _call_lock_type_name(node.value) or "Lock"
            self._record(f"lock_assignment:{lock_type}")
            if isinstance(node.target, ast.Name):
                self.lock_vars.add(node.target.id)
            self.evidence.replacements_made += 1
            return _placeholder_stmt()
        return node

    def _with_item_is_lock(self, item: ast.withitem) -> bool:
        ctx = item.context_expr
        if _is_lock_factory_call(ctx):
            return True
        if isinstance(ctx, ast.Name) and ctx.id in self.lock_vars:
            return True
        if isinstance(ctx, ast.Attribute):
            if ctx.attr in _LOCK_TYPE_NAMES:
                return True
            if isinstance(ctx.value, ast.Name) and ctx.value.id in {"self", "cls"}:
                if ctx.attr.lower() in {"lock", "mutex"}:
                    return True
        if isinstance(ctx, ast.Name) and ctx.id.lower() in {"lock", "mutex", "_lock"}:
            return True
        return False

    def visit_With(self, node: ast.With) -> ast.AST:
        if any(self._with_item_is_lock(item) for item in node.items):
            self._record("with_lock_context")
            self.evidence.replacements_made += 1
            new_body = [_placeholder_stmt(), *node.body]
            if len(new_body) == 1:
                return new_body[0]
            return new_body
        return self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> ast.stmt | None:
        if _is_acquire_or_release_call(node.value):
            self._record("acquire_release_call")
            self.evidence.replacements_made += 1
            return _placeholder_stmt()
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        if node.attr in {"acquire", "release"}:
            self._record(f".{node.attr}(")
        return node


def _inject_sentinel_comments(code: str) -> str:
    lines: list[str] = []
    for line in code.splitlines():
        if _SENTINEL_CALL in line:
            indent = line[: len(line) - len(line.lstrip())]
            lines.append(f"{indent}{LOCK_MARKER_PLACEHOLDER}")
        else:
            lines.append(line)
    return "\n".join(lines) + ("\n" if code.endswith("\n") else "")


def _record_text(evidence: StripEvidence, marker: str) -> None:
    if marker not in evidence.markers_removed:
        evidence.markers_removed.append(marker)


def _text_lock_marker_strip(code: str, evidence: StripEvidence) -> str:
    lines_out: list[str] = []
    for line in code.splitlines():
        replaced = line
        for marker_name, pattern in _LOCK_TEXT_PATTERNS:
            if pattern.search(replaced):
                stripped = replaced.strip()
                if stripped == LOCK_MARKER_PLACEHOLDER or _SENTINEL_CALL in replaced:
                    break
                _record_text(evidence, marker_name)
                indent = replaced[: len(replaced) - len(replaced.lstrip())]
                replaced = f"{indent}{LOCK_MARKER_PLACEHOLDER}"
                evidence.replacements_made += 1
                break
        lines_out.append(replaced)
    result = "\n".join(lines_out)
    if code.endswith("\n"):
        result += "\n"
    return result


def lock_marker_strip(code: str) -> tuple[str, StripEvidence]:
    """Observer ablation: remove obvious lock/synchronization markers (not semantics-preserving)."""
    evidence = StripEvidence()
    tree = ast.parse(code)
    stripper = _LockMarkerStripper(evidence)
    tree = stripper.visit(tree)
    ast.fix_missing_locations(tree)
    if isinstance(tree, list):
        module = ast.Module(body=tree, type_ignores=[])
        ast.fix_missing_locations(module)
        result = ast.unparse(module)
    else:
        result = ast.unparse(tree)
    result = _inject_sentinel_comments(result)
    result = _text_lock_marker_strip(result, evidence)
    return result, evidence


def strip_code(code: str, level: StripLevel | str, *, dimension: str | None = None) -> str:
    """Apply stripping transforms cumulatively up to the requested level."""
    stripped, _ = strip_code_with_evidence(code, level, dimension=dimension)
    return stripped


def strip_code_with_evidence(
    code: str,
    level: StripLevel | str,
    *,
    dimension: str | None = None,
) -> tuple[str, dict[str, Any] | None]:
    """Apply stripping; returns evidence dict for lock_marker_strip, else None."""
    if isinstance(level, str):
        level = StripLevel(level)

    preserve_names = preserve_names_for_dimension(dimension)

    if level == StripLevel.RAW:
        return code, None

    if level == StripLevel.LOCK_MARKER_STRIP:
        stripped, evidence = lock_marker_strip(code)
        return stripped, evidence.to_dict()

    result = code
    idx = _STRIP_ORDER.index(level)
    for step in _STRIP_ORDER[1 : idx + 1]:
        if step == StripLevel.NO_COMMENTS:
            result = _remove_comments(result)
        elif step == StripLevel.RENAMED:
            result = _rename_identifiers(result, preserve_names=preserve_names)
        elif step == StripLevel.NO_IMPORTS:
            result = _materialize_imports(result)
            result = _remove_imports(result)
        elif step == StripLevel.FORMAT_NORMALIZED:
            result = _format_normalize(result)
    return result, None


def strip_file(path: str, level: StripLevel | str) -> str:
    stripped, _ = strip_file_with_evidence(path, level)
    return stripped


def strip_file_with_evidence(
    path: str,
    level: StripLevel | str,
    *,
    sidecar_path: Path | None = None,
) -> tuple[str, dict[str, Any] | None]:
    source = Path(path)
    code = source.read_text(encoding="utf-8")
    stripped, evidence = strip_code_with_evidence(code, level)

    if evidence is not None:
        out = sidecar_path or (source.parent / f"{source.name}.lock_marker_strip.json")
        payload = {
            "source": str(source),
            "level": StripLevel.LOCK_MARKER_STRIP.value,
            **evidence,
        }
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return stripped, evidence


def write_strip_sidecar(
    sidecar_path: Path,
    *,
    source: str,
    level: str,
    evidence: dict[str, Any],
) -> None:
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"source": source, "level": level, **evidence}
    sidecar_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
