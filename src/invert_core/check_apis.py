from __future__ import annotations

import typer

from invert.check_apis import check_api_keys, format_api_check

__all__ = ["check_api_keys", "format_api_check", "run_check_apis"]


def run_check_apis(models: list[str], *, strict: bool = False) -> int:
    """Return exit code: 0 if all keys present (or strict=False), else 1."""
    results = check_api_keys(models)
    typer.echo(format_api_check(results))
    if not strict:
        return 0
    missing = [m for m, ok in results.items() if not ok and m != "local_stub"]
    return 1 if missing else 0
