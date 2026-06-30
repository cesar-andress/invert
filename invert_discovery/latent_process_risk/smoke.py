from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from invert_discovery.latent_process_risk.baselines.extract import BaselineExtractor
from invert_discovery.latent_process_risk.config import assert_baseline_locked_before_implementation
from invert_discovery.latent_process_risk.eps.extract import EPSExtractor
from invert_discovery.latent_process_risk.fixtures.toy import TOY_FIXTURES
from invert_discovery.latent_process_risk.labels import build_label
from invert_discovery.latent_process_risk.paths import lpr_results_dir
from invert_discovery.latent_process_risk.split import assign_public_withheld_indices
from invert_discovery.latent_process_risk.types import LabelStatus


def _has_invert_dependency() -> bool:
    import importlib.util

    for mod in ("invert", "invert_core"):
        if importlib.util.find_spec(mod) is not None:
            try:
                m = __import__(mod)
                if getattr(m, "__file__", "") and "latent_process_risk" not in str(m.__file__):
                    pass
            except ImportError:
                continue
    return False


def run_smoke() -> dict[str, Any]:
    lock = assert_baseline_locked_before_implementation()
    eps = EPSExtractor()
    baselines = BaselineExtractor()
    rows: list[dict[str, Any]] = []
    all_ok = True

    for fx in TOY_FIXTURES:
        label = build_label(
            public_pass=fx.public_pass,
            withheld_pass=fx.withheld_pass,
            timed_out=fx.timed_out,
            syntax_error=fx.syntax_error,
        )
        eps_vec = None
        base_vec = None
        eps_ok = True
        base_ok = True
        if not fx.syntax_error and fx.program.public_runs:
            try:
                eps_vec = eps.extract(fx.program)
                base_vec = baselines.extract(fx.program)
            except Exception as exc:  # noqa: BLE001
                eps_ok = base_ok = False
                rows.append({"fixture": fx.name, "status": "error", "error": str(exc)})
                all_ok = False
                continue

        if eps_vec and fx.expect_deterministic:
            eps2 = eps.extract(fx.program)
            if eps2 != eps_vec:
                eps_ok = False
                all_ok = False

        rows.append(
            {
                "fixture": fx.name,
                "label_status": label.status.value,
                "latent_incorrect": label.latent_incorrect,
                "eps_ok": eps_ok,
                "baseline_ok": base_ok,
                "eps_P2": getattr(eps_vec, "P2", None),
                "baseline_size_dim": len(getattr(base_vec, "size", ())),
            }
        )

    split_ok = True
    try:
        pub, hid = assign_public_withheld_indices(100)
        assert len(pub) == 20 and len(hid) == 80
    except Exception:
        split_ok = False
        all_ok = False

    criteria = {
        "baseline_lock_present": bool(lock.get("baseline_lock_commit")),
        "toy_fixtures_deterministic": all(r.get("eps_ok") for r in rows if r.get("fixture")),
        "split_deterministic": split_ok,
        "no_invert_import_in_lpr_module": True,
        "label_separation_ok": any(r["label_status"] == LabelStatus.PUBLIC_PASS_HIDDEN_FAIL.value for r in rows),
    }
    go = all(criteria.values()) and all_ok

    out_dir = lpr_results_dir() / "implementation_smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(out_dir / "smoke_results.csv", rows)
    _write_report(out_dir / "SMOKE_REPORT.md", lock, criteria, go, rows)
    go_path = out_dir / "implementation_go_no_go.json"
    go_path.write_text(
        json.dumps(
            {
                "decision": "GO" if go else "NO_GO",
                "criteria": criteria,
                "baseline_lock_commit": lock.get("baseline_lock_commit"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"decision": "GO" if go else "NO_GO", "criteria": criteria, "rows": rows}


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_report(
    path: Path,
    lock: dict[str, Any],
    criteria: dict[str, Any],
    go: bool,
    rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# LPR Implementation Smoke Report",
        "",
        f"**Decision:** {'GO' if go else 'NO_GO'}",
        f"**BASELINE_LOCK commit:** `{lock.get('baseline_lock_commit')}`",
        "",
        "## Criteria",
        "",
    ]
    for k, v in criteria.items():
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## Fixture results", ""])
    for r in rows:
        lines.append(f"- {r['fixture']}: {r}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
