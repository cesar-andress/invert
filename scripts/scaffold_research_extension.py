#!/usr/bin/env python3
"""Scaffold research extension preflight experiment folders."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "research_extension"

HYPOTHESES = [
    {
        "id": "H01_temperature_process_diversity",
        "title": "Temperature and process trace diversity",
        "rq": "Does sampling temperature increase bounded process-trace diversity among valid artifacts?",
        "classes": ["C", "D", "E"],
        "generation": True,
        "est_calls": 1440,
        "go": "GO if >=2 dynamic classes show Shannon H increase >=0.5 bits from T=0 to T=0.8 for >=2 models with valid_rate>=0.5",
    },
    {
        "id": "H02_neutral_prompt_process_bias",
        "title": "Neutral-prompt process pole bias",
        "rq": "Do models default to stable process poles when pole names are omitted from prompts?",
        "classes": ["C", "D", "E"],
        "generation": True,
        "est_calls": 810,
        "go": "GO if >=2 models show >=70% default to one detected pole on >=2 classes with valid_rate>=0.4",
    },
    {
        "id": "H03_reasoning_vs_coder_process",
        "title": "Reasoning vs coder process strategies",
        "rq": "Do reasoning models differ in bounded process traces from coder models at matched validity?",
        "classes": ["C", "D", "E"],
        "generation": True,
        "est_calls": 540,
        "go": "GO if fingerprint divergence significant on >=2 classes with matched valid_n>=30",
    },
    {
        "id": "H04_self_consistency_process_collapse",
        "title": "Self-consistency process diversity collapse",
        "rq": "Does pass@k-style selection reduce process diversity among valid samples?",
        "classes": ["C", "D", "E"],
        "generation": True,
        "est_calls": 720,
        "go": "GO if median diversity_loss>=0.3 bits on >=2 classes",
    },
    {
        "id": "H05_repair_process_drift",
        "title": "Repair-induced process drift",
        "rq": "Does automated repair preserve process signatures when fixing invalid artifacts?",
        "classes": ["C", "D", "E"],
        "generation": True,
        "est_calls": 400,
        "go": "GO if >=15% repaired-valid artifacts flip process pole or fingerprint",
    },
    {
        "id": "H06_specialized_vs_base_process",
        "title": "Code-specialized vs base process monoculture",
        "rq": "Do code-specialized models show lower process diversity than base instruct models?",
        "classes": ["C", "D", "E"],
        "generation": True,
        "est_calls": 540,
        "go": "GO if coder richness <= 0.5 * base richness on >=2 classes",
    },
    {
        "id": "H07_model_size_process_diversity",
        "title": "Model size and process diversity",
        "rq": "How does model scale relate to process trace diversity?",
        "classes": ["C", "D", "E"],
        "generation": True,
        "est_calls": 810,
        "go": "GO if monotonic richness-size trend with r^2>=0.5 across >=3 sizes",
    },
    {
        "id": "H08_cross_class_process_coupling",
        "title": "Cross-class process coupling",
        "rq": "Are model process fingerprints correlated across C/D/E?",
        "classes": ["derived"],
        "generation": False,
        "est_calls": 0,
        "go": "GO if |Spearman rho|>=0.5 between >=2 class pairs for >=3 models",
    },
    {
        "id": "H09_rep_scaling_hidden_diversity",
        "title": "Repetition scaling at T=0",
        "rq": "Does increasing N reveal latent diversity without raising temperature?",
        "classes": ["C", "D", "E"],
        "generation": True,
        "est_calls": 1350,
        "go": "GO if N=30 richness >= 2x N=5 on >=2 deterministic poles",
    },
    {
        "id": "H10_instruction_tuning_monoculture",
        "title": "Instruction tuning process monoculture",
        "rq": "Do instruct/chat checkpoints show lower process diversity than base models?",
        "classes": ["derived"],
        "generation": True,
        "est_calls": 540,
        "go": "GO if instruct richness < base on >=3 classes",
    },
]

RUN_PREFLIGHT = '''#!/usr/bin/env python3
"""Preflight for {hypothesis_id}."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from invert_discovery.research_extension.common import (
    check_ollama_models,
    check_path_exists,
    experiment_dir,
    project_root,
    results_dir,
    write_preflight_result,
)

HYPOTHESIS_ID = "{hypothesis_id}"


def main() -> int:
    exp = experiment_dir(HYPOTHESIS_ID)
    checks = [
        check_path_exists(exp / "config.yaml", "config.yaml"),
        check_path_exists(exp / "schema.csv", "schema.csv"),
        check_path_exists(exp / "go_no_go.json", "go_no_go.json"),
        check_path_exists(ROOT / "invert_discovery/ecology/fingerprint.py", "fingerprint_module"),
        check_path_exists(
            ROOT / "results/discovery/process_trace_diversity_preflight/ecology_cells.csv",
            "prior_preflight_data",
        ),
    ]
{extra_checks}
    ok = all(c.get("ok", False) for c in checks)
    notes = [
        "{rq}",
        "Preflight only — no full generation in this script.",
        "Estimated generation calls: {est_calls}",
    ]
    write_preflight_result(
        HYPOTHESIS_ID,
        status="ready" if ok else "blocked",
        checks=checks,
        notes=notes,
        estimated_generation_calls={est_calls},
    )
    print(json.dumps({{"status": "ready" if ok else "blocked", "hypothesis": HYPOTHESIS_ID}}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''

README_TEMPLATE = """# {hypothesis_id}: {title}

## Research question

{rq}

## INVERT classes

{classes}

## Status

Preflight scaffold only. No full generation executed.

## Files

- `config.yaml` — experiment skeleton
- `schema.csv` — output column schema
- `go_no_go.json` — decision criteria
- `run_preflight.py` — lightweight readiness checks

## Constraints

- Do not modify frozen Core v2 detectors or frozen runs
- No human annotation; no LLM judges; no external adapters

## Go/no-go

{go}
"""

CONFIG_TEMPLATE = """study_id: {hypothesis_id}
title: "{title}"
status: preflight

constraints:
  modify_frozen_detectors: false
  modify_frozen_runs: false
  human_annotation: false
  llm_judges: false
  external_adapters: false

invert_classes: {classes_yaml}

generation:
  enabled: {gen_enabled}
  estimated_calls: {est_calls}
  models:
    - ollama:qwen2.5-coder:14b
    - ollama:devstral:latest
    - ollama:qwen3-coder:30b
  temperature: null  # see experiment design
  repetitions: null

outputs:
  results_dir: results/research_extension/{hypothesis_id}
  fingerprints_csv: fingerprints.csv
  summary_csv: summary.csv
  report_md: REPORT.md
"""

SCHEMA = """column,type,description
study_id,string,hypothesis identifier
class_id,string,INVERT class C D E or derived
task_id,string,Family1 task id
requested_pole,string,prompt-assigned pole or neutral
model,string,generator model id
temperature,float,sampling temperature if applicable
rep,int,repetition index
strip_level,string,detector strip level
artifact_id,string,unique artifact key
valid_artifact,bool,behavioral gate passed
detector_correct,bool,recovered requested pole
fingerprint,string,SHA256 of normalized bounded trace
richness,float,unique_fingerprints over n
shannon_entropy,float,Shannon H of fingerprints in cell
simpson_diversity,float,Simpson index
"""

for h in HYPOTHESES:
    d = EXP / h["id"]
    d.mkdir(parents=True, exist_ok=True)
    classes_str = ", ".join(h["classes"])
    (d / "README.md").write_text(
        README_TEMPLATE.format(
            hypothesis_id=h["id"],
            title=h["title"],
            rq=h["rq"],
            classes=classes_str,
            go=h["go"],
        ),
        encoding="utf-8",
    )
    classes_yaml = "\n".join(f"    - {c}" for c in h["classes"])
    (d / "config.yaml").write_text(
        CONFIG_TEMPLATE.format(
            hypothesis_id=h["id"],
            title=h["title"],
            classes_yaml=classes_yaml,
            gen_enabled=str(h["generation"]).lower(),
            est_calls=h["est_calls"],
        ),
        encoding="utf-8",
    )
    (d / "schema.csv").write_text(SCHEMA, encoding="utf-8")
    (d / "go_no_go.json").write_text(
        json.dumps(
            {
                "hypothesis_id": h["id"],
                "recommended": "pending",
                "criterion": h["go"],
                "full_study_recommended": False,
                "paper_placement": "pending_preflight_execution",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    extra = ""
    if h["generation"]:
        extra = """    checks.append(check_ollama_models([
        "ollama:qwen2.5-coder:14b",
        "ollama:devstral:latest",
        "ollama:qwen3-coder:30b",
    ]))"""
    else:
        extra = '    checks.append({"check": "generation_required", "ok": True, "note": "frozen-data only"})'
    script = RUN_PREFLIGHT.format(
        hypothesis_id=h["id"],
        extra_checks=extra,
        rq=h["rq"],
        est_calls=h["est_calls"],
    )
    rp = d / "run_preflight.py"
    rp.write_text(script, encoding="utf-8")
    rp.chmod(0o755)

print(f"Scaffolded {len(HYPOTHESES)} experiments under {EXP}")
