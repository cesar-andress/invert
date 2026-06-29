from __future__ import annotations

import hashlib
import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any

from invert.schemas import DIMENSION_NAMES


class ModelClient(ABC):
    def __init__(self, model: str, temperature: float = 0.2, **kwargs: Any):
        self.model = model
        self.temperature = temperature
        self.extra = kwargs

    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...


class LocalStubClient(ModelClient):
    """Deterministic stub for end-to-end pipeline testing without API keys."""

    def generate(self, prompt: str) -> str:
        if "blind intent recovery judge" in prompt.lower():
            return self._recovery_response(prompt)
        return self._code_response(prompt)

    def _code_response(self, prompt: str) -> str:
        task_match = re.search(r"Implement the following programming task", prompt)
        dim_section = re.search(
            r"## Intent dimensions\nApply ALL of the following.*?\n(.*?)\n\n## Output",
            prompt,
            re.DOTALL,
        )
        dims = dim_section.group(1).strip() if dim_section else ""
        seed = hashlib.md5(prompt.encode()).hexdigest()[:8]
        return (
            f"# Stub implementation (seed={seed})\n"
            f"def solve(*args, **kwargs):\n"
            f'    """Generated stub for smoke test."""\n'
            f"    # Intent snapshot:\n"
            + "".join(f"    # {line}\n" for line in dims.splitlines())
            + "    return None\n"
        )

    def _recovery_response(self, prompt: str) -> str:
        code_match = re.search(r"## Generated code\n(.*?)\n\n## Dimensions", prompt, re.DOTALL)
        code = code_match.group(1) if code_match else ""
        result: dict[str, dict[str, float | str]] = {}
        for dim in DIMENSION_NAMES:
            tag_match = re.search(rf"# invert:{dim}=(v[01])", code)
            if tag_match:
                value = tag_match.group(1)
                confidence = 0.85
            else:
                h = int(hashlib.md5(f"{dim}:{code}".encode()).hexdigest(), 16)
                value = "v0" if h % 2 == 0 else "v1"
                confidence = 0.5 + (h % 50) / 100.0
            result[dim] = {"value": value, "confidence": round(confidence, 2)}
        return json.dumps(result)


class OpenAIClient(ModelClient):
    def generate(self, prompt: str) -> str:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""


class AnthropicClient(ModelClient):
    def generate(self, prompt: str) -> str:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


class GoogleClient(ModelClient):
    def generate(self, prompt: str) -> str:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set")
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(
            prompt,
            generation_config={"temperature": self.temperature},
        )
        return response.text


PROVIDER_CLASSES: dict[str, type[ModelClient]] = {
    "openai": OpenAIClient,
    "anthropic": AnthropicClient,
    "google": GoogleClient,
    "local_stub": LocalStubClient,
}


def create_client(provider: str, config: dict[str, Any]) -> ModelClient:
    if provider not in PROVIDER_CLASSES:
        raise ValueError(f"Unknown provider: {provider}")
    cls = PROVIDER_CLASSES[provider]
    return cls(
        model=config.get("model", "unknown"),
        temperature=config.get("temperature", 0.2),
    )
