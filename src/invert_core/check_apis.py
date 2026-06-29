from __future__ import annotations

import typer

from invert.check_apis import check_api_keys
from invert_core.models import check_ollama_model, is_ollama_model

__all__ = ["check_api_keys", "run_check_apis", "check_core_api_keys"]


def check_core_api_keys(models: list[str]) -> tuple[dict[str, bool], dict[str, str]]:
    results: dict[str, bool] = {}
    details: dict[str, str] = {}
    cloud_models = [m for m in models if not is_ollama_model(m)]
    if cloud_models:
        cloud_results = check_api_keys(cloud_models)
        results.update(cloud_results)
        for model in cloud_models:
            details[model] = "key found" if cloud_results[model] else "key missing"
    for model in models:
        if not is_ollama_model(model):
            continue
        ok, detail = check_ollama_model(model)
        results[model] = ok
        details[model] = "ok" if ok else detail
    return results, details


def format_core_api_check(results: dict[str, bool], models: list[str], details: dict[str, str]) -> str:
    lines = []
    for model in models:
        ok = results.get(model, False)
        detail = details.get(model, "key missing" if not ok else "ok")
        lines.append(f"{model}: {detail}")
    return "\n".join(lines)


def run_check_apis(models: list[str], *, strict: bool = False) -> int:
    """Return exit code: 0 if checks pass (ollama always enforced)."""
    results, details = check_core_api_keys(models)
    typer.echo(format_core_api_check(results, models, details))
    failures = [m for m in models if not results.get(m, False)]
    if strict and failures:
        return 1
    ollama_failures = [m for m in failures if is_ollama_model(m)]
    if ollama_failures:
        return 1
    return 0
