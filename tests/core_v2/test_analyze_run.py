from __future__ import annotations

from pathlib import Path

import pytest

from invert_core.analyze_run import run_analyze_run
from invert_core.generate import run_core_v2_generation
from invert_core.pilot_config import CoreV2PilotConfig
from invert_core.tasks import project_root


def test_valid_only_summary_excludes_invalid_behavioral(tmp_path: Path) -> None:
    config = tmp_path / "pilot.yaml"
    config.write_text(
        """
run:
  name: test_valid_only
  overwrite: true
family: F1
dimension: euler_vs_rk4
tasks:
  file: data/core_v2/tasks/euler_rk4_tasks.json
  include:
    - exponential_decay
generation:
  models:
    - local_stub
  repetitions: 1
  language: python
  pure_implementation: true
  models_config: configs/models.yaml
methods:
  - euler
  - rk4
stripping:
  levels:
    - raw
""",
        encoding="utf-8",
    )
    root = project_root()
    pilot = CoreV2PilotConfig.from_yaml(config, root)
    run_core_v2_generation(pilot, dry_run=False)

    # Inject one invalid artifact (syntax error) alongside valid stub outputs.
    bad_path = (
        root
        / "data/core_v2/code/test_valid_only/local_stub/exponential_decay/euler/rep_99.py"
    )
    bad_path.parent.mkdir(parents=True, exist_ok=True)
    bad_path.write_text("def integrate_ode( broken\n", encoding="utf-8")

    result = run_analyze_run("test_valid_only", root, config_path=config)
    assert result.valid_summary_path.exists()

    raw_valid = [
        r
        for r in result.valid_summary_rows
        if r["strip_level"] == "raw" and r["task_id"] == "exponential_decay"
    ]
    euler_valid = next(r for r in raw_valid if r["method"] == "euler")
    assert euler_valid["valid_n"] == "1"
    assert euler_valid["valid_detector_accuracy"] == "1.0000"

    raw_all = [r for r in result.summary_rows if r["strip_level"] == "raw"]
    euler_all = next(r for r in raw_all if r["method"] == "euler")
    assert int(euler_all["all_generated_n"]) >= 2
    assert euler_all["all_generated_detector_accuracy"] != euler_valid["valid_detector_accuracy"]

    invalid = next(r for r in result.detection_rows if r["rep"] == 99)
    assert invalid["valid_artifact"] == "false"
    assert invalid["parsed"] == "false"

    # cleanup
    for sub in ("raw", "code", "stripped"):
        run_dir = root / "data" / "core_v2" / sub / "test_valid_only"
        if run_dir.exists():
            for p in sorted(run_dir.rglob("*"), reverse=True):
                if p.is_file():
                    p.unlink()
            for p in sorted(run_dir.rglob("*"), reverse=True):
                if p.is_dir():
                    p.rmdir()
    results_run = root / "results" / "core_v2" / "runs" / "test_valid_only"
    if results_run.exists():
        for p in results_run.glob("*"):
            p.unlink()
        results_run.rmdir()


def test_detection_csv_columns() -> None:
    root = project_root()
    run = "core_v2_euler_rk4_pilot_local_001"
    code_root = root / "data" / "core_v2" / "code" / run
    if not code_root.exists():
        pytest.skip("local pilot artifacts not present")
    result = run_analyze_run(run, root)
    assert result.detection_rows
    row = result.detection_rows[0]
    for field in (
        "run",
        "model",
        "task_id",
        "method",
        "rep",
        "strip_level",
        "parsed",
        "behavioral_pass",
        "valid_artifact",
        "detected_method",
        "detector_correct",
        "ambiguous",
    ):
        assert field in row
