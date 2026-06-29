from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DETECTOR_REL_PATHS = {
    "integration.py": Path("src/invert_core/detectors/integration.py"),
    "quadrature.py": Path("src/invert_core/detectors/quadrature.py"),
    "eager_lazy.py": Path("src/invert_core/detectors/eager_lazy.py"),
    "bfs_dfs.py": Path("src/invert_core/detectors/bfs_dfs.py"),
    "deterministic_randomized.py": Path(
        "src/invert_core/detectors/deterministic_randomized.py"
    ),
}

STRIPPING_REL_PATH = Path("src/invert_core/stripping.py")

DYNAMIC_DIMENSIONS = frozenset({
    "eager_vs_lazy",
    "bfs_vs_dfs",
    "deterministic_vs_randomized",
})

FROZEN_NOTE = "detectors frozen before this generalization run"


def is_generalization_run_name(run_name: str) -> bool:
    return "generalization" in run_name


def is_frozen_generalization_run(run_dir: Path) -> bool:
    return (run_dir / "frozen_detector_metadata.json").exists()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit(project_root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def detector_file_hashes(project_root: Path, *, dimension: str | None = None) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for name, rel_path in DETECTOR_REL_PATHS.items():
        path = project_root / rel_path
        if path.exists():
            hashes[name] = _file_sha256(path)
    if dimension in DYNAMIC_DIMENSIONS:
        stripping_path = project_root / STRIPPING_REL_PATH
        if stripping_path.exists():
            hashes["stripping.py"] = _file_sha256(stripping_path)
    return hashes


def write_frozen_detector_metadata(
    results_dir: Path,
    *,
    project_root: Path,
    run_name: str,
    dimension: str,
) -> Path:
    payload = {
        "run_name": run_name,
        "dimension": dimension,
        "git_commit": _git_commit(project_root),
        "detector_files_hash": detector_file_hashes(project_root, dimension=dimension),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": FROZEN_NOTE,
    }
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / "frozen_detector_metadata.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out_path


def maybe_write_frozen_detector_metadata(
    run_name: str,
    project_root: Path,
    dimension: str,
) -> Path | None:
    if not is_generalization_run_name(run_name):
        return None
    results_dir = project_root / "results" / "core_v2" / "runs" / run_name
    return write_frozen_detector_metadata(
        results_dir,
        project_root=project_root,
        run_name=run_name,
        dimension=dimension,
    )
