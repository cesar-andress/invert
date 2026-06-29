from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from invert.aggregate import run_aggregate
from invert.check_apis import check_api_keys, format_api_check
from invert.audit_redacted import run_audit_redacted
from invert.compare_baselines import run_compare_baselines
from invert.config import PilotConfig, load_run_metadata
from invert.diagnose import run_diagnose
from invert.generate import run_generation
from invert.keyword_baseline import run_keyword_baseline
from invert.manifest import run_manifest
from invert.manifestation_recovery import run_manifestation_recovery_analysis
from invert.category_b_forensic import run_category_b_forensic
from invert.reanalyze_strict import run_reanalyze_strict
from invert.plot import run_plot
from invert.recover import run_recovery
from invert.redact_proxies import run_redact_proxies
from invert.strip_proxies import run_strip_proxies

app = typer.Typer(help="INVERT minimal falsification prototype")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASKS = PROJECT_ROOT / "data" / "intents" / "tasks.json"
DEFAULT_MODELS_CFG = PROJECT_ROOT / "configs" / "models.yaml"
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "results"


def _resolve_config_path(config: Path) -> Path:
    if config.is_absolute():
        return config
    candidate = PROJECT_ROOT / config
    if candidate.exists():
        return candidate
    return config


@app.command()
def generate(
    models: str = typer.Option("local_stub", help="Comma-separated generator model names"),
    tasks: Path = typer.Option(DEFAULT_TASKS, help="Path to tasks JSON"),
    repetitions: int = typer.Option(1, help="Repetitions per condition"),
    data_dir: Path = typer.Option(DEFAULT_DATA_DIR, help="Data directory"),
    models_config: Path = typer.Option(DEFAULT_MODELS_CFG, help="Models config YAML"),
    config: Optional[Path] = typer.Option(None, "--config", help="Pilot config YAML"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print plan without API calls"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files"),
) -> None:
    pilot: PilotConfig | None = None
    task_ids: list[str] | None = None
    dimension_ids: list[str] | None = None
    max_generations: int | None = None
    do_overwrite = overwrite

    if config is not None:
        config_path = _resolve_config_path(config)
        pilot = PilotConfig.from_yaml(config_path, PROJECT_ROOT)
        model_list = pilot.generator_models
        tasks = pilot.tasks_file
        repetitions = pilot.repetitions
        task_ids = pilot.task_ids
        dimension_ids = pilot.dimension_ids
        max_generations = pilot.max_generations
        if not overwrite:
            do_overwrite = pilot.overwrite
    else:
        model_list = [m.strip() for m in models.split(",") if m.strip()]

    run_generation(
        model_list,
        tasks,
        repetitions,
        data_dir,
        models_config,
        task_ids=task_ids,
        dimension_ids=dimension_ids,
        dry_run=dry_run,
        overwrite=do_overwrite,
        max_generations=max_generations,
        pilot=pilot,
        project_root=PROJECT_ROOT,
    )
    if not dry_run:
        typer.echo(f"Generation complete for models: {', '.join(model_list)}")


@app.command()
def recover(
    judge: str = typer.Option("local_stub", help="Judge model name"),
    models: str = typer.Option("local_stub", help="Comma-separated generator models to recover"),
    tasks: Path = typer.Option(DEFAULT_TASKS, help="Path to tasks JSON"),
    data_dir: Path = typer.Option(DEFAULT_DATA_DIR, help="Data directory"),
    models_config: Path = typer.Option(DEFAULT_MODELS_CFG, help="Models config YAML"),
    config: Optional[Path] = typer.Option(None, "--config", help="Pilot config YAML"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files"),
    stripped: bool = typer.Option(False, "--stripped", help="Recover from proxy-stripped code"),
    redacted: bool = typer.Option(False, "--redacted", help="Recover from redacted code"),
) -> None:
    task_ids: list[str] | None = None
    dimension_ids: list[str] | None = None
    do_overwrite = overwrite
    judge_model = judge
    model_list: list[str]

    if config is not None:
        config_path = _resolve_config_path(config)
        pilot = PilotConfig.from_yaml(config_path, PROJECT_ROOT)
        judge_model = pilot.judge_models[0]
        model_list = pilot.generator_models
        tasks = pilot.tasks_file
        task_ids = pilot.task_ids
        dimension_ids = pilot.dimension_ids
        if not overwrite:
            do_overwrite = pilot.overwrite
    else:
        model_list = [m.strip() for m in models.split(",") if m.strip()]

    run_recovery(
        judge_model,
        model_list,
        tasks,
        data_dir,
        models_config,
        task_ids=task_ids,
        dimension_ids=dimension_ids,
        overwrite=do_overwrite,
        stripped=stripped,
        redacted=redacted,
    )
    if redacted:
        label = " (redacted)"
    elif stripped:
        label = " (stripped)"
    else:
        label = ""
    typer.echo(f"Recovery complete with judge: {judge_model}{label}")


@app.command()
def aggregate(
    data_dir: Path = typer.Option(DEFAULT_DATA_DIR, help="Data directory"),
    results_dir: Path = typer.Option(DEFAULT_RESULTS_DIR, help="Results directory"),
    run: Optional[str] = typer.Option(None, "--run", help="Run name for filtered aggregation"),
    stripped: bool = typer.Option(False, "--stripped", help="Aggregate stripped recovery results"),
    redacted: bool = typer.Option(False, "--redacted", help="Aggregate redacted recovery results"),
) -> None:
    generator_models: list[str] | None = None
    task_ids: list[str] | None = None
    judge_models: list[str] | None = None
    dimension_ids: list[str] | None = None

    if run is not None:
        metadata = load_run_metadata(PROJECT_ROOT, run)
        results_dir = PROJECT_ROOT / "results" / "runs" / run
        generator_models = metadata.get("generator_models")
        task_ids = metadata.get("tasks")
        judge_models = metadata.get("judge_models")
        dimension_ids = metadata.get("dimensions")

    run_aggregate(
        data_dir,
        results_dir,
        generator_models=generator_models,
        task_ids=task_ids,
        judge_models=judge_models,
        dimension_ids=dimension_ids,
        stripped=stripped,
        redacted=redacted,
    )
    if redacted:
        suffix = "_redacted"
    elif stripped:
        suffix = "_stripped"
    else:
        suffix = ""
    typer.echo(f"Aggregated results written to {results_dir} (recovery{suffix}.csv)")


@app.command()
def plot(
    results_dir: Path = typer.Option(DEFAULT_RESULTS_DIR, help="Results directory"),
    run: Optional[str] = typer.Option(None, "--run", help="Run name for run-specific plot"),
    stripped: bool = typer.Option(False, "--stripped", help="Plot stripped recovery heatmap"),
    redacted: bool = typer.Option(False, "--redacted", help="Plot redacted recovery heatmap"),
) -> None:
    if run is not None:
        results_dir = PROJECT_ROOT / "results" / "runs" / run
    run_plot(results_dir, stripped=stripped, redacted=redacted)
    if redacted:
        suffix = "_redacted"
    elif stripped:
        suffix = "_stripped"
    else:
        suffix = ""
    typer.echo(f"Heatmap written to {results_dir / f'identifiability_heatmap{suffix}.png'}")


@app.command()
def diagnose(
    run: str = typer.Option(..., "--run", help="Run name to diagnose"),
    stripped: bool = typer.Option(False, "--stripped", help="Diagnose stripped recovery results"),
    redacted: bool = typer.Option(False, "--redacted", help="Diagnose redacted recovery results"),
) -> None:
    if redacted:
        suffix = "_redacted"
    elif stripped:
        suffix = "_stripped"
    else:
        suffix = ""
    recovery_csv = PROJECT_ROOT / "results" / "runs" / run / f"recovery{suffix}.csv"
    run_diagnose(recovery_csv)


@app.command("keyword-baseline")
def keyword_baseline_cmd(
    run: str = typer.Option(..., "--run", help="Run name for keyword baseline"),
    data_dir: Path = typer.Option(DEFAULT_DATA_DIR, help="Data directory"),
) -> None:
    run_keyword_baseline(PROJECT_ROOT, run, data_dir)


@app.command("compare-baselines")
def compare_baselines_cmd(
    run: str = typer.Option(..., "--run", help="Run name for baseline comparison"),
) -> None:
    run_compare_baselines(PROJECT_ROOT, run)


@app.command("strip-proxies")
def strip_proxies_cmd(
    run: str = typer.Option(..., "--run", help="Run name for proxy stripping"),
    data_dir: Path = typer.Option(DEFAULT_DATA_DIR, help="Data directory"),
) -> None:
    run_strip_proxies(PROJECT_ROOT, run, data_dir)


@app.command("redact-proxies")
def redact_proxies_cmd(
    run: str = typer.Option(..., "--run", help="Run name for strict proxy redaction"),
    data_dir: Path = typer.Option(DEFAULT_DATA_DIR, help="Data directory"),
) -> None:
    run_redact_proxies(PROJECT_ROOT, run, data_dir)


@app.command("audit-redacted")
def audit_redacted_cmd(
    run: str = typer.Option(..., "--run", help="Run name for redacted leakage audit"),
    data_dir: Path = typer.Option(DEFAULT_DATA_DIR, help="Data directory"),
) -> None:
    run_audit_redacted(PROJECT_ROOT, run, data_dir)


@app.command()
def manifest(
    run: str = typer.Option(..., "--run", help="Run name for manifestation diagnostics"),
    data_dir: Path = typer.Option(DEFAULT_DATA_DIR, help="Data directory"),
) -> None:
    run_manifest(PROJECT_ROOT, run, data_dir)


@app.command("analyze-manifestation-recovery")
def analyze_manifestation_recovery_cmd(
    run: str = typer.Option(..., "--run", help="Run name for manifestation–recovery analysis"),
) -> None:
    run_manifestation_recovery_analysis(PROJECT_ROOT, run)


@app.command("reanalyze-strict")
def reanalyze_strict_cmd(
    run: str = typer.Option(..., "--run", help="Run name for strict manifestation–recovery reanalysis"),
) -> None:
    run_reanalyze_strict(PROJECT_ROOT, run)


@app.command("analyze-category-b")
def analyze_category_b_cmd(
    run: str = typer.Option(..., "--run", help="Run name for Category B forensic analysis"),
) -> None:
    run_category_b_forensic(PROJECT_ROOT, run)


@app.command("check-apis")
def check_apis_cmd(
    models: str = typer.Option(..., "--models", help="Comma-separated provider names"),
) -> None:
    model_list = [m.strip() for m in models.split(",") if m.strip()]
    results = check_api_keys(model_list)
    typer.echo(format_api_check(results))
    missing = [m for m, ok in results.items() if not ok and m != "local_stub"]
    if missing:
        raise typer.Exit(1)


@app.command("smoke-test")
def smoke_test() -> None:
    """Run end-to-end pipeline with local_stub."""
    import subprocess
    import sys

    script = PROJECT_ROOT / "scripts" / "smoke_test.py"
    result = subprocess.run([sys.executable, str(script)], cwd=PROJECT_ROOT)
    raise typer.Exit(result.returncode)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
