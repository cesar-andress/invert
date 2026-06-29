from __future__ import annotations

import os

PROVIDER_ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
}


def check_api_keys(models: list[str]) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for model in models:
        if model == "local_stub":
            results[model] = True
            continue
        env_key = PROVIDER_ENV_KEYS.get(model)
        if env_key is None:
            results[model] = False
            continue
        value = os.environ.get(env_key, "")
        results[model] = bool(value.strip())
    return results


def format_api_check(results: dict[str, bool]) -> str:
    lines = []
    for model, found in results.items():
        status = "key found" if found else "key missing"
        lines.append(f"{model}: {status}")
    return "\n".join(lines)
