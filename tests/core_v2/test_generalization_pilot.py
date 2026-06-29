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
EAGER_LAZY_CONFIG = project_root() / "configs" / "core_v2_generalization_local_eager_lazy.yaml"
BFS_DFS_CONFIG = project_root() / "configs" / "core_v2_generalization_local_bfs_dfs.yaml"
DET_RAND_CONFIG = (
    project_root() / "configs" / "core_v2_generalization_local_deterministic_randomized.yaml"
)


@pytest.mark.parametrize(
    ("config_path", "run_name", "expected", "n_models"),
    [
        (EULER_CONFIG, "core_v2_generalization_local_euler_rk4_001", 90, 3),
        (QUADRATURE_CONFIG, "core_v2_generalization_local_quadrature_001", 90, 3),
        (EAGER_LAZY_CONFIG, "core_v2_generalization_local_eager_lazy_001", 120, 4),
        (BFS_DFS_CONFIG, "core_v2_generalization_local_bfs_dfs_001", 120, 4),
        (
            DET_RAND_CONFIG,
            "core_v2_generalization_local_deterministic_randomized_001",
            120,
            4,
        ),
    ],
)
def test_generalization_expected_generations(
    config_path: Path, run_name: str, expected: int, n_models: int
) -> None:
    pilot = CoreV2PilotConfig.from_yaml(config_path, project_root())
    items = plan_core_v2_generations(pilot, pilot.load_tasks())
    assert pilot.run_name == run_name
    assert pilot.repetitions == 5
    assert len(pilot.models) == n_models
    assert pilot.expected_generations() == expected
    assert len(items) == expected


def test_generalization_run_name_detection() -> None:
    assert is_generalization_run_name("core_v2_generalization_local_euler_rk4_001")
    assert is_generalization_run_name("core_v2_generalization_local_eager_lazy_001")
    assert is_generalization_run_name("core_v2_generalization_local_bfs_dfs_001")
    assert is_generalization_run_name(
        "core_v2_generalization_local_deterministic_randomized_001"
    )
    assert not is_generalization_run_name("core_v2_euler_rk4_pilot_local_001")


def test_write_frozen_detector_metadata(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    det_dir = root / "src/invert_core/detectors"
    det_dir.mkdir(parents=True)
    (det_dir / "integration.py").write_text("# integration\n", encoding="utf-8")
    (det_dir / "quadrature.py").write_text("# quadrature\n", encoding="utf-8")
    (det_dir / "eager_lazy.py").write_text("# eager_lazy\n", encoding="utf-8")
    (det_dir / "bfs_dfs.py").write_text("# bfs_dfs\n", encoding="utf-8")
    (root / "src/invert_core/stripping.py").write_text("# stripping\n", encoding="utf-8")

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
    assert "eager_lazy.py" in meta["detector_files_hash"]
    assert "bfs_dfs.py" in meta["detector_files_hash"]
    assert "stripping.py" not in meta["detector_files_hash"]


def test_frozen_metadata_includes_eager_lazy_detector_hash() -> None:
    root = project_root()
    run_dir = root / "results" / "core_v2" / "runs" / "_test_frozen_eager_lazy_meta"
    run_dir.mkdir(parents=True, exist_ok=True)
    path = write_frozen_detector_metadata(
        run_dir,
        project_root=root,
        run_name="core_v2_generalization_local_eager_lazy_001",
        dimension="eager_vs_lazy",
    )
    meta = json.loads(path.read_text(encoding="utf-8"))
    assert meta["dimension"] == "eager_vs_lazy"
    assert meta["git_commit"] != "unknown"
    eager_hash = meta["detector_files_hash"]["eager_lazy.py"]
    strip_hash = meta["detector_files_hash"]["stripping.py"]
    assert len(eager_hash) == 64
    assert len(strip_hash) == 64
    import hashlib

    expected = hashlib.sha256(
        (root / "src/invert_core/detectors/eager_lazy.py").read_bytes()
    ).hexdigest()
    expected_strip = hashlib.sha256(
        (root / "src/invert_core/stripping.py").read_bytes()
    ).hexdigest()
    assert eager_hash == expected
    assert strip_hash == expected_strip
    path.unlink()
    run_dir.rmdir()


def test_frozen_metadata_includes_bfs_dfs_and_stripping_hashes() -> None:
    root = project_root()
    run_dir = root / "results" / "core_v2" / "runs" / "_test_frozen_bfs_dfs_meta"
    run_dir.mkdir(parents=True, exist_ok=True)
    path = write_frozen_detector_metadata(
        run_dir,
        project_root=root,
        run_name="core_v2_generalization_local_bfs_dfs_001",
        dimension="bfs_vs_dfs",
    )
    meta = json.loads(path.read_text(encoding="utf-8"))
    assert meta["dimension"] == "bfs_vs_dfs"
    assert meta["git_commit"] != "unknown"
    import hashlib

    bfs_hash = meta["detector_files_hash"]["bfs_dfs.py"]
    strip_hash = meta["detector_files_hash"]["stripping.py"]
    assert len(bfs_hash) == 64
    assert len(strip_hash) == 64
    expected_bfs = hashlib.sha256(
        (root / "src/invert_core/detectors/bfs_dfs.py").read_bytes()
    ).hexdigest()
    expected_strip = hashlib.sha256(
        (root / "src/invert_core/stripping.py").read_bytes()
    ).hexdigest()
    assert bfs_hash == expected_bfs
    assert strip_hash == expected_strip
    path.unlink()
    run_dir.rmdir()


def test_frozen_metadata_includes_deterministic_randomized_and_stripping_hashes() -> None:
    root = project_root()
    run_dir = root / "results" / "core_v2" / "runs" / "_test_frozen_det_rand_meta"
    run_dir.mkdir(parents=True, exist_ok=True)
    path = write_frozen_detector_metadata(
        run_dir,
        project_root=root,
        run_name="core_v2_generalization_local_deterministic_randomized_001",
        dimension="deterministic_vs_randomized",
    )
    meta = json.loads(path.read_text(encoding="utf-8"))
    assert meta["dimension"] == "deterministic_vs_randomized"
    assert meta["git_commit"] != "unknown"
    import hashlib

    det_hash = meta["detector_files_hash"]["deterministic_randomized.py"]
    strip_hash = meta["detector_files_hash"]["stripping.py"]
    assert len(det_hash) == 64
    assert len(strip_hash) == 64
    expected_det = hashlib.sha256(
        (root / "src/invert_core/detectors/deterministic_randomized.py").read_bytes()
    ).hexdigest()
    expected_strip = hashlib.sha256(
        (root / "src/invert_core/stripping.py").read_bytes()
    ).hexdigest()
    assert det_hash == expected_det
    assert strip_hash == expected_strip
    path.unlink()
    run_dir.rmdir()


def test_maybe_write_frozen_metadata_for_eager_lazy_generalization(tmp_path: Path) -> None:
    from invert_core.frozen_detector import maybe_write_frozen_detector_metadata

    root = tmp_path / "repo"
    root.mkdir()
    det_dir = root / "src/invert_core/detectors"
    det_dir.mkdir(parents=True)
    for name in ("integration.py", "quadrature.py", "eager_lazy.py", "bfs_dfs.py"):
        (det_dir / name).write_text(f"# {name}\n", encoding="utf-8")
    (root / "src/invert_core").mkdir(parents=True, exist_ok=True)
    (root / "src/invert_core/stripping.py").write_text("# stripping\n", encoding="utf-8")

    path = maybe_write_frozen_detector_metadata(
        "core_v2_generalization_local_eager_lazy_001",
        root,
        "eager_vs_lazy",
    )
    assert path is not None
    meta = json.loads(path.read_text(encoding="utf-8"))
    assert "eager_lazy.py" in meta["detector_files_hash"]
    assert "stripping.py" in meta["detector_files_hash"]


def test_maybe_write_frozen_metadata_for_bfs_dfs_generalization(tmp_path: Path) -> None:
    from invert_core.frozen_detector import maybe_write_frozen_detector_metadata

    root = tmp_path / "repo"
    root.mkdir()
    det_dir = root / "src/invert_core/detectors"
    det_dir.mkdir(parents=True)
    for name in ("integration.py", "quadrature.py", "eager_lazy.py", "bfs_dfs.py"):
        (det_dir / name).write_text(f"# {name}\n", encoding="utf-8")
    (root / "src/invert_core").mkdir(parents=True, exist_ok=True)
    (root / "src/invert_core/stripping.py").write_text("# stripping\n", encoding="utf-8")

    path = maybe_write_frozen_detector_metadata(
        "core_v2_generalization_local_bfs_dfs_001",
        root,
        "bfs_vs_dfs",
    )
    assert path is not None
    meta = json.loads(path.read_text(encoding="utf-8"))
    assert "bfs_dfs.py" in meta["detector_files_hash"]
    assert "stripping.py" in meta["detector_files_hash"]


def test_maybe_write_frozen_metadata_for_deterministic_randomized_generalization(
    tmp_path: Path,
) -> None:
    from invert_core.frozen_detector import maybe_write_frozen_detector_metadata

    root = tmp_path / "repo"
    root.mkdir()
    det_dir = root / "src/invert_core/detectors"
    det_dir.mkdir(parents=True)
    for name in (
        "integration.py",
        "quadrature.py",
        "eager_lazy.py",
        "bfs_dfs.py",
        "deterministic_randomized.py",
    ):
        (det_dir / name).write_text(f"# {name}\n", encoding="utf-8")
    (root / "src/invert_core").mkdir(parents=True, exist_ok=True)
    (root / "src/invert_core/stripping.py").write_text("# stripping\n", encoding="utf-8")

    path = maybe_write_frozen_detector_metadata(
        "core_v2_generalization_local_deterministic_randomized_001",
        root,
        "deterministic_vs_randomized",
    )
    assert path is not None
    meta = json.loads(path.read_text(encoding="utf-8"))
    assert "deterministic_randomized.py" in meta["detector_files_hash"]
    assert "stripping.py" in meta["detector_files_hash"]


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
