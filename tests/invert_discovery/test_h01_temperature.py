from invert_discovery.temperature_diversity.metrics import (
    bootstrap_shannon_ci,
    cell_metrics_from_fingerprints,
    is_monotonic_non_decreasing,
    shannon_entropy,
    simpson_diversity,
)


def test_bootstrap_ci_nontrivial() -> None:
    fps = ["a", "b", "a", "c", "b"]
    point, lo, hi = bootstrap_shannon_ci(fps, n_resamples=200, seed=1)
    assert lo <= point <= hi
    assert hi > 0


def test_monotonic() -> None:
    assert is_monotonic_non_decreasing([0.0, 0.1, 0.2])
    assert not is_monotonic_non_decreasing([0.2, 0.1, 0.3])
