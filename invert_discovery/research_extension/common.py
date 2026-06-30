from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def experiment_dir(hypothesis_id: str) -> Path:
    return project_root() / "experiments" / "research_extension" / hypothesis_id


def results_dir(hypothesis_id: str) -> Path:
    return project_root() / "results" / "research_extension" / hypothesis_id


def write_preflight_result(
    hypothesis_id: str,
    *,
    status: str,
    checks: list[dict[str, Any]],
    notes: list[str],
    estimated_generation_calls: int | None = None,
) -> Path:
    out = results_dir(hypothesis_id)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "hypothesis_id": hypothesis_id,
        "preflight_status": status,
        "checks": checks,
        "notes": notes,
        "estimated_generation_calls": estimated_generation_calls,
    }
    path = out / "preflight_result.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def check_path_exists(path: Path, label: str) -> dict[str, Any]:
    return {"check": label, "path": str(path), "ok": path.exists()}


def check_ollama_models(models: list[str]) -> dict[str, Any]:
    try:
        import urllib.request

        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        available = {m.get("name", "") for m in data.get("models", [])}
        missing = []
        for spec in models:
            name = spec.split(":", 1)[-1] if spec.startswith("ollama:") else spec
            if not any(name in a for a in available):
                missing.append(spec)
        return {
            "check": "ollama_models",
            "ok": len(missing) == 0,
            "missing": missing,
            "available_count": len(available),
        }
    except Exception as exc:
        return {"check": "ollama_models", "ok": False, "error": str(exc)}
