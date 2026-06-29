from __future__ import annotations

from invert_core.analyze_run import _build_model_rankings, _classify_model_failure
from invert_core.generate import run_core_v2_generation
from invert_core.pilot_config import CoreV2PilotConfig, plan_core_v2_generations
from invert_core.tasks import project_root


def test_sweep_pilot_expected_generations() -> None:
    config = project_root() / "configs" / "core_v2_euler_rk4_pilot_local_sweep.yaml"
    pilot = CoreV2PilotConfig.from_yaml(config, project_root())
    items = plan_core_v2_generations(pilot, pilot.load_tasks())
    assert pilot.expected_generations() == 90
    assert len(items) == 90
    assert len(pilot.models) == 5


def test_sweep_dry_run_paths(capsys) -> None:
    config = project_root() / "configs" / "core_v2_euler_rk4_pilot_local_sweep.yaml"
    pilot = CoreV2PilotConfig.from_yaml(config, project_root())
    run_core_v2_generation(pilot, dry_run=True)
    out = capsys.readouterr().out
    assert "Total expected generations: 90" in out
    assert "core_v2_euler_rk4_pilot_local_sweep_001" in out
    assert "ollama__qwen3-coder__30b" in out
    assert "ollama__devstral__latest" in out
    assert "ollama__qwen2_5-coder__14b" in out


def test_model_ranking_orders_f11_first() -> None:
    detection_rows = [
        {
            "model": "m_fail",
            "strip_level": "raw",
            "valid_artifact": "true",
            "detector_correct": "true",
            "ambiguous": "false",
        },
        {
            "model": "m_fail",
            "strip_level": "format_normalized",
            "valid_artifact": "true",
            "detector_correct": "false",
            "ambiguous": "false",
        },
        {
            "model": "m_pass",
            "strip_level": "raw",
            "valid_artifact": "true",
            "detector_correct": "true",
            "ambiguous": "false",
        },
        {
            "model": "m_pass",
            "strip_level": "format_normalized",
            "valid_artifact": "true",
            "detector_correct": "true",
            "ambiguous": "false",
        },
    ]
    # pad m_pass to meet valid_n >= 12
    for i in range(11):
        detection_rows.append(
            {
                "model": "m_pass",
                "strip_level": "raw",
                "valid_artifact": "true",
                "detector_correct": "true",
                "ambiguous": "false",
            }
        )
        detection_rows.append(
            {
                "model": "m_pass",
                "strip_level": "format_normalized",
                "valid_artifact": "true",
                "detector_correct": "true",
                "ambiguous": "false",
            }
        )

    model_f11 = {
        "m_pass": {"survives": True},
        "m_fail": {"survives": False},
    }
    rankings = _build_model_rankings(detection_rows, model_f11)
    assert rankings[0]["model"] == "m_pass"
    assert rankings[0]["f1_1_survives"] is True
    assert rankings[0]["rank"] == 1
    assert "valid_ambiguous_rate_format_normalized" in rankings[0]


def test_classify_invalid_generation_vs_detector_collapse() -> None:
    assert _classify_model_failure({"valid_n": 6}, {"survives": False}) == "invalid_generation"
    assert (
        _classify_model_failure(
            {"valid_n": 18},
            {
                "survives": False,
                "raw_accuracy": 0.5,
                "format_normalized_accuracy": 1.0,
                "raw_ambiguous_rate": 0.0,
            },
        )
        == "detector_collapse"
    )
    assert (
        _classify_model_failure(
            {"valid_n": 18},
            {
                "survives": True,
                "raw_accuracy": 1.0,
                "format_normalized_accuracy": 1.0,
                "raw_ambiguous_rate": 0.0,
            },
        )
        == "f1_1_support"
    )
