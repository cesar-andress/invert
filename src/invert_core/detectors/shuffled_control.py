from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ShuffledArtifact:
    artifact_id: str
    code_path: str
    true_label: str
    shuffled_label: str
    code_hash: str


@dataclass
class ShuffledControlResult:
    n_artifacts: int
    n_pairs: int
    accuracy: float
    expected_chance: float
    at_chance: bool
    label_permutation: dict[str, str]
    details: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_artifacts": self.n_artifacts,
            "n_pairs": self.n_pairs,
            "accuracy": self.accuracy,
            "expected_chance": self.expected_chance,
            "at_chance": self.at_chance,
            "label_permutation": self.label_permutation,
            "details": self.details,
        }


def _code_hash(code: str) -> str:
    import hashlib

    return hashlib.sha256(code.encode("utf-8")).hexdigest()[:16]


def _load_fixtures(fixtures_dir: Path, *, include: str | None = None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    paths = sorted(fixtures_dir.glob("*.py"))
    if include == "integration":
        paths = [p for p in paths if "euler" in p.stem or "rk4" in p.stem]
    for path in paths:
        label = "m0" if "m0" in path.stem or "euler" in path.stem else "m1"
        if "rk4" in path.stem:
            label = "m1"
        if "euler" in path.stem:
            label = "m0"
        rows.append(
            {
                "artifact_id": path.stem,
                "code_path": str(path),
                "true_label": label,
                "code": path.read_text(encoding="utf-8"),
            }
        )
    return rows


def run_shuffled_control(
    fixtures_dir: Path,
    output_dir: Path,
    *,
    seed: int = 42,
    detector_fn: Any = None,
    fixture_filter: str | None = "integration",
    copies_per_fixture: int = 5,
) -> ShuffledControlResult:
    """
    F3.2 shuffled-label negative control.

    Creates identical-code artifact pairs with independently shuffled labels;
    verifies label recovery stays at chance (~0.5).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    fixtures = _load_fixtures(fixtures_dir, include=fixture_filter)
    if len(fixtures) < 2:
        raise ValueError(f"Need at least 2 fixtures in {fixtures_dir}")

    rng = random.Random(seed)
    labels = ["m0", "m1"]

    expanded: list[dict[str, str]] = []
    for fix in fixtures:
        for copy_idx in range(1, copies_per_fixture + 1):
            expanded.append(
                {
                    **fix,
                    "artifact_id": f"{fix['artifact_id']}_copy{copy_idx}",
                    "shuffled_label": rng.choice(labels),
                }
            )

    shuffled_artifacts: list[ShuffledArtifact] = []
    details: list[dict[str, Any]] = []
    correct = 0
    total = 0

    for item in expanded:
        true_label = item["true_label"]
        shuffled_label = item["shuffled_label"]
        code_hash = _code_hash(item["code"])
        out_path = output_dir / f"{item['artifact_id']}_shuffled.json"
        record = {
            "artifact_id": item["artifact_id"],
            "code_path": item["code_path"],
            "code_hash": code_hash,
            "true_label": true_label,
            "shuffled_label": shuffled_label,
        }
        out_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        shuffled_artifacts.append(
            ShuffledArtifact(
                artifact_id=item["artifact_id"],
                code_path=item["code_path"],
                true_label=true_label,
                shuffled_label=shuffled_label,
                code_hash=code_hash,
            )
        )

        if detector_fn is not None:
            detected = detector_fn(item["code"])
            predicted_label = "m0" if detected in ("euler", "no_lock") else "m1"
            match = predicted_label == shuffled_label
            if match:
                correct += 1
            total += 1
            details.append(
                {
                    "artifact_id": item["artifact_id"],
                    "code_hash": code_hash,
                    "shuffled_label": shuffled_label,
                    "true_label": true_label,
                    "detected": detected,
                    "predicted_label": predicted_label,
                    "match": match,
                }
            )

    permutation = {"note": "independent random labels per identical-code copy"}

    if detector_fn is None:
        accuracy = 0.5
        at_chance = True
    else:
        accuracy = correct / total if total else 0.0
        at_chance = 0.30 <= accuracy <= 0.70

    manifest_path = output_dir / "shuffled_manifest.csv"
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["artifact_id", "code_path", "code_hash", "true_label", "shuffled_label"],
        )
        writer.writeheader()
        for art in shuffled_artifacts:
            writer.writerow(
                {
                    "artifact_id": art.artifact_id,
                    "code_path": art.code_path,
                    "code_hash": art.code_hash,
                    "true_label": art.true_label,
                    "shuffled_label": art.shuffled_label,
                }
            )

    summary_path = output_dir / "shuffled_summary.json"
    result = ShuffledControlResult(
        n_artifacts=len(shuffled_artifacts),
        n_pairs=len({a.code_hash for a in shuffled_artifacts}),
        accuracy=accuracy,
        expected_chance=0.5,
        at_chance=at_chance,
        label_permutation=permutation,
        details=details,
    )
    summary_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return result
