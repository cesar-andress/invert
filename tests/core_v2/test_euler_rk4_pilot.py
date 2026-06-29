from __future__ import annotations

import json
from pathlib import Path

import pytest

from invert_core.analyze_run import run_analyze_run
from invert_core.behavioral import run_behavioral_oracle
from invert_core.generate import run_core_v2_generation
from invert_core.ode_tasks import load_ode_tasks
from invert_core.pilot_config import CoreV2PilotConfig, plan_core_v2_generations
from invert_core.prompts import METHOD_OPERATIONAL, build_generation_prompt, build_stub_code
from invert_core.tasks import project_root


PILOT_CONFIG = project_root() / "configs" / "core_v2_euler_rk4_pilot.yaml"
TASKS_FILE = project_root() / "data" / "core_v2" / "tasks" / "euler_rk4_tasks.json"


def test_pilot_expected_generations() -> None:
    pilot = CoreV2PilotConfig.from_yaml(PILOT_CONFIG, project_root())
    items = plan_core_v2_generations(pilot, pilot.load_tasks())
    assert pilot.expected_generations() == 72
    assert len(items) == 72


def test_dry_run_prints_paths(capsys) -> None:
    pilot = CoreV2PilotConfig.from_yaml(PILOT_CONFIG, project_root())
    run_core_v2_generation(pilot, dry_run=True)
    out = capsys.readouterr().out
    assert "Total expected generations: 72" in out
    assert "core_v2_euler_rk4_pilot_001" in out
    assert "data/core_v2/raw/core_v2_euler_rk4_pilot_001" in out


def test_prompts_include_operational_definitions() -> None:
    tasks = load_ode_tasks(TASKS_FILE)
    for task in tasks:
        euler_prompt = build_generation_prompt(task, "euler")
        rk4_prompt = build_generation_prompt(task, "rk4")
        assert METHOD_OPERATIONAL["euler"] in euler_prompt
        assert METHOD_OPERATIONAL["rk4"] in rk4_prompt
        assert "scipy" in euler_prompt.lower()
        assert "integrate_ode" in euler_prompt


@pytest.mark.parametrize("method", ["euler", "rk4"])
def test_stub_codes_pass_behavioral_oracle(method: str) -> None:
    tasks = load_ode_tasks(TASKS_FILE)
    for task in tasks:
        code = build_stub_code(task, method)
        result = run_behavioral_oracle(code, task)
        assert result.parsed, task.task_id
        assert result.behavioral_pass, f"{task.task_id}: {result.error}"


def test_local_stub_generation_and_analyze_run(tmp_path: Path) -> None:
    config = tmp_path / "pilot.yaml"
    config.write_text(
        """
run:
  name: test_run_local
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
    - no_comments
""",
        encoding="utf-8",
    )
    root = project_root()
    pilot = CoreV2PilotConfig.from_yaml(config, root)
    run_core_v2_generation(pilot, dry_run=False)

    result = run_analyze_run("test_run_local", root, config_path=config)
    assert result.detection_path.exists()
    assert result.summary_path.exists()
    assert result.valid_summary_path.exists()
    assert result.report_path.exists()
    assert result.stats["n_artifacts"] == 2
    assert len(result.detection_rows) == 4  # 2 methods x 2 strip levels
    raw_rows = [r for r in result.detection_rows if r["strip_level"] == "raw"]
    assert all(r["detector_correct"] == "true" for r in raw_rows)
    assert all(r["valid_artifact"] == "true" for r in raw_rows)

    # cleanup generated test data
    for sub in ("raw", "code", "stripped"):
        run_dir = root / "data" / "core_v2" / sub / "test_run_local"
        if run_dir.exists():
            for p in sorted(run_dir.rglob("*"), reverse=True):
                if p.is_file():
                    p.unlink()
            for p in sorted(run_dir.rglob("*"), reverse=True):
                if p.is_dir():
                    p.rmdir()
            if run_dir.exists():
                run_dir.rmdir()
    results_run = root / "results" / "core_v2" / "runs" / "test_run_local"
    if results_run.exists():
        for p in results_run.glob("*"):
            p.unlink()
        results_run.rmdir()
