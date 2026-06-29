from __future__ import annotations

import json
from pathlib import Path

import pytest

from invert_core.frozen_detector import (
    FROZEN_NOTE,
    is_frozen_generalization_run,
    is_generalization_run_name,
    write_frozen_detector_metadata,
)
from invert_core.pilot_config import CoreV2PilotConfig, plan_core_v2_generations
from invert_core.tasks import project_root

EULER_CONFIG = project_root() / "configs" / "core_v2_generalization_local_euler_rk4.yaml"
QUADRATURE_CONFIG = project_root() / "configs" / "core_v2_generalization_local_quadrature.yaml"


@pytest.mark.parametrize(
    ("config_path", "run_name", "expected"),
    [
        (EULER_CONFIG, "core_v2_generalization_local_euler_rk4_001", 90),
        (QUADRATURE_CONFIG, "core_v2_generalization_local_quadrature_001", 90),
    ],
)
def test_generalization_expected_generations(
    config_path: Path, run_name: str, expected: int
) -> None:
    pilot = CoreV2PilotConfig.from_yaml(config_path, project_root())
    items = plan_core_v2_generations(pilot, pilot.load_tasks())
    assert pilot.run_name == run_name
    assert pilot.repetitions == 5
    assert len(pilot.models) == 3
    assert pilot.expected_generations() == expected
    assert len(items) == expected


def test_generalization_run_name_detection() -> None:
    assert is_generalization_run_name("core_v2_generalization_local_euler_rk4_001")
    assert not is_generalization_run_name("core_v2_euler_rk4_pilot_local_001")


def test_write_frozen_detector_metadata(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    det_dir = root / "src/invert_core/detectors"
    det_dir.mkdir(parents=True)
    (det_dir / "integration.py").write_text("# integration\n", encoding="utf-8")
    (det_dir / "quadrature.py").write_text("# quadrature\n", encoding="utf-8")

    run_dir = tmp_path / "results" / "core_v2" / "runs" / "core_v2_generalization_local_euler_rk4_001"
    path = write_frozen_detector_metadata(
        run_dir,
        project_root=root,
        run_name="core_v2_generalization_local_euler_rk4_001",
        dimension="euler_vs_rk4",
    )
    assert path.exists()
    assert is_frozen_generalization_run(run_dir)
    meta = json.loads(path.read_text(encoding="utf-8"))
    assert meta["run_name"] == "core_v2_generalization_local_euler_rk4_001"
    assert meta["dimension"] == "euler_vs_rk4"
    assert meta["note"] == FROZEN_NOTE
    assert "integration.py" in meta["detector_files_hash"]
    assert "quadrature.py" in meta["detector_files_hash"]


def test_summarize_report_lists_run_inventory(tmp_path: Path) -> None:
    from invert_core.summarize_core_v2 import run_summarize_core_v2

    runs_root = tmp_path / "results" / "core_v2" / "runs"
    dev_dir = runs_root / "core_v2_euler_rk4_pilot_local_001"
    frozen_dir = runs_root / "core_v2_generalization_local_euler_rk4_001"
    dev_dir.mkdir(parents=True)
    frozen_dir.mkdir(parents=True)

    (dev_dir / "metadata.json").write_text(
        '{"dimension":"euler_vs_rk4"}', encoding="utf-8"
    )
    (frozen_dir / "metadata.json").write_text(
        '{"dimension":"euler_vs_rk4"}', encoding="utf-8"
    )
    write_frozen_detector_metadata(
        frozen_dir,
        project_root=project_root(),
        run_name="core_v2_generalization_local_euler_rk4_001",
        dimension="euler_vs_rk4",
    )

    summary_fields = [
        "model",
        "task_id",
        "method",
        "strip_level",
        "all_generated_n",
        "all_generated_detector_accuracy",
        "all_generated_behavioral_pass_rate",
        "all_generated_ambiguous_rate",
    ]
    valid_fields = [
        "model",
        "task_id",
        "method",
        "strip_level",
        "valid_n",
        "valid_detector_accuracy",
        "valid_ambiguous_rate",
    ]
    row = {
        "model": "model_a",
        "task_id": "t1",
        "method": "euler",
        "strip_level": "raw",
        "all_generated_n": "10",
        "all_generated_detector_accuracy": "1.0000",
        "all_generated_behavioral_pass_rate": "1.0000",
        "all_generated_ambiguous_rate": "0.0000",
        "valid_n": "10",
        "valid_detector_accuracy": "1.0000",
        "valid_ambiguous_rate": "0.0000",
    }
    for run in (dev_dir, frozen_dir):
        import csv

        with open(run / "integration_summary.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=summary_fields)
            writer.writeheader()
            writer.writerow({k: row[k] for k in summary_fields})
        with open(run / "integration_valid_only_summary.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=valid_fields)
            writer.writeheader()
            writer.writerow({k: row[k] for k in valid_fields})

    result = run_summarize_core_v2(tmp_path)
    report = result.decision_report_path.read_text(encoding="utf-8")
    assert "## Run inventory" in report
    assert "core_v2_euler_rk4_pilot_local_001" in report
    assert "core_v2_generalization_local_euler_rk4_001" in report
    assert "## Frozen generalization evidence" in report
