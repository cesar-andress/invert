from __future__ import annotations

import csv
from pathlib import Path

import pytest

from invert_core.diagnose_deterministic_randomized import (
    DIAGNOSIS_FIELDS,
    classify_behavioral_failure,
    run_diagnose_deterministic_randomized,
)
from invert_core.deterministic_randomized_behavioral import (
    DeterministicRandomizedBehavioralResult,
    run_deterministic_randomized_behavioral_oracle,
)
from invert_core.deterministic_randomized_tasks import load_deterministic_randomized_tasks
from invert_core.tasks import project_root

RUN = "core_v2_deterministic_randomized_pilot_local_001"
TASKS_FILE = project_root() / "data" / "core_v2" / "tasks" / "deterministic_randomized_tasks.json"


MAP_TRANSFORM_CODE = '''
class ItemProcessor:
    def __init__(self, items, visit_fn, seed=None):
        self.items = items
        self.visit_fn = visit_fn

    def process_all(self):
        return [self.visit_fn(item) for item in sorted(self.items)]
'''


def test_classify_map_transform_as_output_not_expected_set() -> None:
    task = load_deterministic_randomized_tasks(TASKS_FILE)[0]
    result = run_deterministic_randomized_behavioral_oracle(MAP_TRANSFORM_CODE, task)
    category, reason = classify_behavioral_failure(MAP_TRANSFORM_CODE, result, task=task)
    assert result.behavioral_pass is False
    assert category == "output_not_expected_set"
    assert "visit_fn" in reason


def test_diagnose_pilot_run_if_present() -> None:
    run_dir = project_root() / "results" / "core_v2" / "runs" / RUN
    code_root = (
        project_root()
        / "data"
        / "core_v2"
        / "code"
        / RUN
    )
    if not code_root.exists():
        pytest.skip("pilot artifacts not present")

    result = run_diagnose_deterministic_randomized(RUN, project_root())
    assert result.csv_path is not None
    assert result.md_path is not None
    assert result.csv_path.exists()
    assert result.md_path.exists()
    assert len(result.rows) == 120

    with open(result.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == DIAGNOSIS_FIELDS
        rows = list(reader)

    assert all(r["parsed"] == "true" for r in rows)
    assert all(r["behavioral_pass"] == "false" for r in rows)
    assert all(r["captures_visit_fn_return_value"] == "true" for r in rows)
    categories = {r["failure_category"] for r in rows}
    assert categories <= {"output_not_expected_set", "exception_during_execution"}

    md = result.md_path.read_text(encoding="utf-8")
    assert "Prompt/API-contract failure" in md or "visit_fn" in md


def test_diagnose_writes_under_run_dir() -> None:
    run_dir = project_root() / "results" / "core_v2" / "runs" / RUN
    if not (project_root() / "data" / "core_v2" / "code" / RUN).exists():
        pytest.skip("pilot artifacts not present")
    result = run_diagnose_deterministic_randomized(RUN, project_root())
    assert result.csv_path.parent == run_dir
    assert result.md_path.name == "deterministic_randomized_diagnosis.md"
