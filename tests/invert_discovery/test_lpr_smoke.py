from __future__ import annotations

import pytest

from invert_discovery.latent_process_risk.baselines.extract import BaselineExtractor
from invert_discovery.latent_process_risk.config import assert_baseline_locked_before_implementation
from invert_discovery.latent_process_risk.eps.extract import EPSExtractor
from invert_discovery.latent_process_risk.fixtures.toy import TOY_FIXTURES
from invert_discovery.latent_process_risk.labels import build_label
from invert_discovery.latent_process_risk.split import assign_public_withheld_indices
from invert_discovery.latent_process_risk.types import LabelStatus, reject_label_kwargs


def test_baseline_lock_before_implementation() -> None:
    lock = assert_baseline_locked_before_implementation()
    assert lock["baseline_lock_commit"].startswith("b80cc32")


def test_split_deterministic() -> None:
    pub1, hid1 = assign_public_withheld_indices(100)
    pub2, hid2 = assign_public_withheld_indices(100)
    assert pub1 == pub2 == list(range(20))
    assert hid1 == hid2 == list(range(20, 100))


def test_split_insufficient() -> None:
    with pytest.raises(ValueError, match="SPLIT_INSUFFICIENT"):
        assign_public_withheld_indices(50)


def test_no_hidden_label_in_eps_extraction() -> None:
    fx = next(f for f in TOY_FIXTURES if f.name == "public_pass_hidden_pass")
    eps = EPSExtractor()
    with pytest.raises(ValueError, match="Label leakage"):
        eps.extract(fx.program, latent_incorrect=True)


def test_no_hidden_label_in_baseline_extraction() -> None:
    fx = next(f for f in TOY_FIXTURES if f.name == "public_pass_hidden_pass")
    base = BaselineExtractor()
    with pytest.raises(ValueError, match="Label leakage"):
        base.extract(fx.program, y=1)


def test_eps_extraction_shape() -> None:
    fx = next(f for f in TOY_FIXTURES if f.name == "deterministic_execution")
    vec = EPSExtractor().extract(fx.program)
    assert len(vec.P1) >= 1
    assert len(vec.P4) == 3
    assert len(vec.P7) == 32


def test_baseline_extraction_shape() -> None:
    fx = next(f for f in TOY_FIXTURES if f.name == "deterministic_execution")
    vec = BaselineExtractor().extract(fx.program)
    assert len(vec.size) == 7
    assert len(vec.ast) == 29
    assert len(vec.bytecode) == 34
    assert vec.embedding_available is False


def test_label_construction_latent() -> None:
    latent = build_label(public_pass=True, withheld_pass=False)
    ok = build_label(public_pass=True, withheld_pass=True)
    assert latent.status == LabelStatus.PUBLIC_PASS_HIDDEN_FAIL
    assert latent.latent_incorrect is True
    assert ok.latent_incorrect is False


def test_eps_reproducibility() -> None:
    fx = next(f for f in TOY_FIXTURES if f.name == "deterministic_execution")
    eps = EPSExtractor()
    assert eps.extract(fx.program) == eps.extract(fx.program)


def test_unstable_fixture_has_output_instability() -> None:
    fx = next(f for f in TOY_FIXTURES if f.name == "unstable_execution")
    vec = EPSExtractor().extract(fx.program)
    assert vec.P2 > 0.0


def test_no_invert_dependency_in_lpr_imports() -> None:
    import invert_discovery.latent_process_risk.eps.extract as eps_mod
    import invert_discovery.latent_process_risk.baselines.extract as base_mod

    assert "invert_core" not in eps_mod.__file__
    assert "invert_core" not in base_mod.__file__


def test_reject_label_kwargs_helper() -> None:
    with pytest.raises(ValueError):
        reject_label_kwargs({"hidden_fail": True})
