from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmbeddingExtractor:
    """Optional embedding baseline — no download required for unit tests."""

    model_id: str = "microsoft/unixcoder-base"
    available: bool = False
    skip_reason: str = "optional; model download not performed in smoke tests"

    def extract(self, source: str) -> tuple[float, ...]:
        if not self.available:
            return tuple(0.0 for _ in range(8))
        raise NotImplementedError("embedding download disabled in skeleton")
