from __future__ import annotations

from invert_discovery.ecology.metrics import cell_ecology_metrics, shannon_entropy, simpson_diversity


def test_monoculture() -> None:
    metrics = cell_ecology_metrics(["a", "a", "a"])
    assert metrics.unique_fingerprints == 1
    assert metrics.richness == metrics.unique_fingerprints / metrics.n
    assert metrics.shannon_entropy == 0.0
    assert metrics.simpson_diversity == 0.0


def test_diversity() -> None:
    metrics = cell_ecology_metrics(["a", "b", "a", "c"])
    assert metrics.n == 4
    assert metrics.unique_fingerprints == 3
    assert metrics.richness == 0.75
    assert metrics.shannon_entropy > 0.0
    assert metrics.simpson_diversity > 0.0


def test_shannon_uniform() -> None:
    counts = {"a": 1, "b": 1}
    assert round(shannon_entropy(counts), 6) == round(0.693147, 6)


def test_simpson_two_equal() -> None:
    counts = {"a": 1, "b": 1}
    assert round(simpson_diversity(counts), 6) == 0.5
