from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from invert.generate import find_code_files
from invert.models import create_client
from invert.prompts import build_recovery_prompt
from invert.schemas import load_tasks, load_yaml


def parse_recovery_json(response: str) -> dict:
    text = response.strip()
    fence = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def parse_code_path(path: Path) -> dict[str, str | int]:
    parts = path.parts
    idx = parts.index("code")
    return {
        "generator_model": parts[idx + 1],
        "task_id": parts[idx + 2],
        "dimension": parts[idx + 3],
        "value": parts[idx + 4],
        "rep": int(path.stem.replace("rep_", "")),
    }


def run_recovery(
    judge: str,
    generator_models: list[str] | None,
    tasks_path: Path,
    data_dir: Path,
    models_config_path: Path,
    *,
    task_ids: list[str] | None = None,
    overwrite: bool = False,
) -> None:
    tasks = {t.task_id: t for t in load_tasks(tasks_path)}
    models_cfg = load_yaml(models_config_path)["providers"]
    if judge not in models_cfg:
        raise ValueError(f"Judge {judge} not found in config")
    client = create_client(judge, models_cfg[judge])

    code_files = find_code_files(data_dir, generator_models, task_ids)
    for code_path in code_files:
        meta = parse_code_path(code_path)
        if meta["task_id"] not in tasks:
            continue
        task = tasks[meta["task_id"]]

        out_dir = (
            data_dir
            / "recovery"
            / meta["generator_model"]
            / meta["task_id"]
            / meta["dimension"]
            / meta["value"]
        )
        out_path = out_dir / f"rep_{meta['rep']}.json"

        if out_path.exists() and not overwrite:
            print(f"SKIP existing: {out_path}")
            continue

        code = code_path.read_text(encoding="utf-8")
        prompt = build_recovery_prompt(code, task)
        response = client.generate(prompt)
        recovered = parse_recovery_json(response)

        record = {
            "generator_model": meta["generator_model"],
            "judge_model": judge,
            "task_id": meta["task_id"],
            "manipulated_dimension": meta["dimension"],
            "true_value": meta["value"],
            "rep": meta["rep"],
            "prompt": prompt,
            "response": response,
            "recovered": recovered,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
