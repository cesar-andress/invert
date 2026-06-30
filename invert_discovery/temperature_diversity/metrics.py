from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class CellMetrics:
    n: int
    unique_fingerprints: int
    richness: float
    dominance: float
    shannon_entropy: float
    simpson_diversity: float
    valid_rate: float
    recovery_rate: float


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
    return 1.0 - sum((c / total) ** 2 for c in counts.values())


def cell_metrics_from_fingerprints(
    fingerprints: Sequence[str],
    *,
    n_generated: int,
    n_valid: int,
    n_recovered: int,
) -> CellMetrics:
    valid_fps = [fp for fp in fingerprints if fp]
    n = len(valid_fps)
    valid_rate = n_valid / n_generated if n_generated else 0.0
    recovery_rate = n_recovered / n_valid if n_valid else 0.0
    if n == 0:
        return CellMetrics(
            n=0,
            unique_fingerprints=0,
            richness=0.0,
            dominance=0.0,
            shannon_entropy=0.0,
            simpson_diversity=0.0,
            valid_rate=valid_rate,
            recovery_rate=recovery_rate,
        )
    counts = Counter(valid_fps)
    unique = len(counts)
    max_freq = max(counts.values())
    return CellMetrics(
        n=n,
        unique_fingerprints=unique,
        richness=unique / n,
        dominance=max_freq / n,
        shannon_entropy=shannon_entropy(counts),
        simpson_diversity=simpson_diversity(counts),
        valid_rate=valid_rate,
        recovery_rate=recovery_rate,
    )


def bootstrap_shannon_ci(
    fingerprints: Sequence[str],
    *,
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Return (point_estimate, ci_low, ci_high) for Shannon entropy."""
    valid = [fp for fp in fingerprints if fp]
    if not valid:
        return 0.0, 0.0, 0.0
    point = shannon_entropy(Counter(valid))
    if len(valid) < 2:
        return point, point, point
    rng = random.Random(seed)
    samples: list[float] = []
    n = len(valid)
    for _ in range(n_resamples):
        draw = [valid[rng.randrange(n)] for _ in range(n)]
        samples.append(shannon_entropy(Counter(draw)))
    samples.sort()
    lo_idx = int((alpha / 2) * n_resamples)
    hi_idx = int((1 - alpha / 2) * n_resamples) - 1
    return point, samples[lo_idx], samples[hi_idx]


def is_monotonic_non_decreasing(values: Sequence[float], tol: float = 1e-9) -> bool:
    if len(values) < 2:
        return False
    for prev, cur in zip(values, values[1:]):
        if cur + tol < prev:
            return False
    return any(cur > prev + tol for prev, cur in zip(values, values[1:]))
