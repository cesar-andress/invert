from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Any


LOCK_PATTERNS = [
    re.compile(r"\bthreading\.Lock\b"),
    re.compile(r"\bthreading\.RLock\b"),
    re.compile(r"\bLock\s*\("),
    re.compile(r"\bRLock\s*\("),
    re.compile(r"\bSemaphore\s*\("),
]


@dataclass
class LockControlResult:
    has_lock: bool
    lock_evidence: list[str]
    method: str  # locked | no_lock | ambiguous

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "has_lock": self.has_lock,
            "evidence": {"lock_signals": self.lock_evidence},
        }


def _with_lock_context(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.With):
            for item in node.items:
                ctx = item.context_expr
                if isinstance(ctx, ast.Call):
                    name = ""
                    if isinstance(ctx.func, ast.Attribute):
                        name = ctx.func.attr
                    elif isinstance(ctx.func, ast.Name):
                        name = ctx.func.id
                    if name in {"Lock", "RLock", "Semaphore"}:
                        return True
    return False


def detect_lock_control(code: str) -> LockControlResult:
    """F2.1 positive trivial control: lock vs no-lock concurrency surface."""
    evidence: list[str] = []

    for pat in LOCK_PATTERNS:
        if pat.search(code):
            evidence.append(f"regex:{pat.pattern}")

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return LockControlResult(
            has_lock=bool(evidence),
            lock_evidence=evidence or ["syntax_error"],
            method="locked" if evidence else "ambiguous",
        )

    if _with_lock_context(tree):
        evidence.append("ast:with_lock_context")

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "Lock",
                "RLock",
                "Semaphore",
            }:
                evidence.append("ast:lock_instantiation")
            elif isinstance(node.func, ast.Name) and node.func.id in {
                "Lock",
                "RLock",
                "Semaphore",
            }:
                evidence.append("ast:lock_instantiation")

    has_lock = len(evidence) > 0
    method = "locked" if has_lock else "no_lock"
    return LockControlResult(has_lock=has_lock, lock_evidence=evidence, method=method)
