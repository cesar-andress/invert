from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from typing import Any


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_TAGS_TIMEOUT = 10
DEFAULT_OLLAMA_GENERATE_TIMEOUT = 900


class ModelClient(ABC):
    def __init__(self, model: str, temperature: float = 0.0, **kwargs: Any):
        self.model = model
        self.temperature = temperature
        self.extra = kwargs

    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...


def parse_ollama_model(spec: str) -> str | None:
    if spec.startswith("ollama:"):
        return spec[len("ollama:") :]
    return None


def is_ollama_model(spec: str) -> bool:
    return parse_ollama_model(spec) is not None


def sanitize_model_for_storage(spec: str) -> str:
    """Map config model spec to filesystem-safe directory name."""
    ollama_model = parse_ollama_model(spec)
    if ollama_model is not None:
        sanitized = ollama_model.replace(".", "_").replace(":", "__")
        return f"ollama__{sanitized}"
    return spec


def _ollama_request(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict | None = None,
    timeout: float = DEFAULT_OLLAMA_TAGS_TIMEOUT,
) -> dict:
    url = f"{base_url.rstrip('/')}{path}"
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def list_ollama_models(
    base_url: str = DEFAULT_OLLAMA_BASE_URL,
    *,
    timeout: float = DEFAULT_OLLAMA_TAGS_TIMEOUT,
) -> list[str]:
    payload = _ollama_request(base_url, "/api/tags", timeout=timeout)
    models: list[str] = []
    for item in payload.get("models", []):
        name = item.get("name")
        if name:
            models.append(name)
    return models


def _model_name_matches(requested: str, available: str) -> bool:
    if requested == available:
        return True
    if available.startswith(f"{requested}:"):
        return True
    if requested.startswith(f"{available}:"):
        return True
    req_base = requested.split(":")[0]
    avail_base = available.split(":")[0]
    return req_base == avail_base and requested.endswith(":latest")


def check_ollama_model(
    spec: str,
    *,
    base_url: str = DEFAULT_OLLAMA_BASE_URL,
    tags_timeout: float = DEFAULT_OLLAMA_TAGS_TIMEOUT,
) -> tuple[bool, str]:
    model = parse_ollama_model(spec)
    if model is None:
        return False, "invalid ollama spec"
    try:
        available = list_ollama_models(base_url, timeout=tags_timeout)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return False, f"ollama unreachable: {exc}"
    if any(_model_name_matches(model, name) for name in available):
        return True, "model available"
    return False, f"model not found (available: {', '.join(available) or 'none'})"


class OllamaClient(ModelClient):
    def __init__(
        self,
        model: str,
        temperature: float = 0.0,
        *,
        base_url: str = DEFAULT_OLLAMA_BASE_URL,
        generate_timeout: float = DEFAULT_OLLAMA_GENERATE_TIMEOUT,
        max_retries: int = 1,
        **kwargs: Any,
    ):
        super().__init__(model=model, temperature=temperature, **kwargs)
        self.base_url = base_url.rstrip("/")
        self.generate_timeout = generate_timeout
        self.max_retries = max(1, int(max_retries))

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                result = _ollama_request(
                    self.base_url,
                    "/api/generate",
                    method="POST",
                    payload=payload,
                    timeout=self.generate_timeout,
                )
                response = result.get("response", "")
                if not isinstance(response, str):
                    raise RuntimeError("Ollama returned unexpected response payload")
                return response
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                time.sleep(min(2 * attempt, 10))
        assert last_error is not None
        raise RuntimeError(
            f"Ollama generate failed for model {self.model!r} after {self.max_retries} "
            f"attempt(s) (timeout={self.generate_timeout}s): {last_error}"
        ) from last_error


def create_core_client(
    model_spec: str,
    models_cfg: dict[str, Any],
) -> ModelClient:
    ollama_model = parse_ollama_model(model_spec)
    if ollama_model is not None:
        ollama_cfg = models_cfg.get("ollama", {})
        return OllamaClient(
            model=ollama_model,
            temperature=float(ollama_cfg.get("temperature", 0)),
            base_url=ollama_cfg.get("base_url", DEFAULT_OLLAMA_BASE_URL),
            generate_timeout=float(
                ollama_cfg.get("generate_timeout_seconds", DEFAULT_OLLAMA_GENERATE_TIMEOUT)
            ),
            max_retries=int(ollama_cfg.get("max_retries", 2)),
        )

    from invert.models import create_client

    if model_spec not in models_cfg:
        raise ValueError(f"Model {model_spec} not found in models config")
    return create_client(model_spec, models_cfg[model_spec])
