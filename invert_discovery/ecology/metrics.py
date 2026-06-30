from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class EcologyMetrics:
    n: int
    unique_fingerprints: int
    richness: float
    dominance: float
    shannon_entropy: float
    simpson_diversity: float


def shannon_entropy(counts: Counter[str]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        if count <= 0:
            continue
        p = count / total
        entropy -= p * math.log(p)
    return entropy


def simpson_diversity(counts: Counter[str]) -> float:
    total = sum(counts.values())
    if total <= 1:
        return 0.0
    sum_sq = sum((count / total) ** 2 for count in counts.values())
    return 1.0 - sum_sq


def cell_ecology_metrics(fingerprints: Sequence[str | None]) -> EcologyMetrics:
    valid = [fp for fp in fingerprints if fp]
    n = len(valid)
    if n == 0:
        return EcologyMetrics(
            n=0,
            unique_fingerprints=0,
            richness=0.0,
            dominance=0.0,
            shannon_entropy=0.0,
            simpson_diversity=0.0,
        )
    counts = Counter(valid)
    unique = len(counts)
    max_freq = max(counts.values())
    return EcologyMetrics(
        n=n,
        unique_fingerprints=unique,
        richness=unique / n,
        dominance=max_freq / n,
        shannon_entropy=shannon_entropy(counts),
        simpson_diversity=simpson_diversity(counts),
    )
