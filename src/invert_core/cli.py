from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

from invert_core.analyze import run_analyze_slice
from invert_core.analyze_run import run_analyze_run
from invert_core.check_apis import run_check_apis
from invert_core.detectors.bfs_dfs import detect_bfs_dfs_file
from invert_core.detectors.deterministic_randomized import detect_deterministic_randomized_file
from invert_core.detectors.eager_lazy import detect_eager_lazy_file
from invert_core.detectors.integration import detect_integration_file
from invert_core.detectors.quadrature import detect_quadrature_file
from invert_core.detectors.shuffled_control import run_shuffled_control
from invert_core.generate import run_core_v2_generation
from invert_core.pilot_config import CoreV2PilotConfig
from invert_core.stripping import StripLevel, strip_file_with_evidence
from invert_core.summarize_core_v2 import run_summarize_core_v2
from invert_core.diagnose_quadrature import run_diagnose_quadrature
from invert_core.diagnose_deterministic_randomized import run_diagnose_deterministic_randomized
from invert_core.tasks import fixtures_dir, project_root, results_dir
from invert_core.verify import verify_fixture_dir

app = typer.Typer(help="INVERT Core v2 — deterministic signature benchmark")


@app.command("check-apis")
def check_apis_cmd(
    models: str = typer.Option(..., "--models", help="Comma-separated provider names"),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Exit 1 if any API key is missing",
    ),
) -> None:
    """Check API key presence (no paid calls)."""
    model_list = [m.strip() for m in models.split(",") if m.strip()]
    code = run_check_apis(model_list, strict=strict)
    if code != 0:
        raise typer.Exit(code)


@app.command("generate")
def generate_cmd(
    config: Path = typer.Option(..., "--config", help="Pilot YAML config"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Plan only, no API calls"),
) -> None:
    """Generate Core v2 artifacts from pilot config."""
    root = project_root()
    pilot = CoreV2PilotConfig.from_yaml(config, root)
    run_core_v2_generation(pilot, dry_run=dry_run)


@app.command("f3-shuffled")
def f3_shuffled(
    seed: int = typer.Option(42, help="RNG seed for label permutation"),
    fixtures: Path | None = typer.Option(None, help="Fixtures directory"),
    output: Path | None = typer.Option(None, help="Output directory"),
) -> None:
    """F3.2 shuffled-label negative control."""
    from invert_core.detectors.integration import detect_integration

    fix_dir = fixtures or fixtures_dir()
    out_dir = output or (results_dir() / "f3_shuffled")

    def detector_fn(code: str) -> str:
        return detect_integration(code, entry_function="integrate_ode").method

    result = run_shuffled_control(fix_dir, out_dir, seed=seed, detector_fn=detector_fn)
    typer.echo(json.dumps(result.to_dict(), indent=2))
    if not result.at_chance:
        typer.echo("WARNING: shuffled control may not be at chance", err=True)
        raise typer.Exit(1)
    typer.echo(f"Wrote manifest to {out_dir}")


@app.command("detect-integration")
def detect_integration_cmd(
    file: Path = typer.Argument(..., help="Python file to analyze"),
    entry_function: str | None = typer.Option(None, help="Entry function name"),
) -> None:
    """Detect Euler vs RK4 integration method."""
    result = detect_integration_file(str(file), entry_function=entry_function)
    typer.echo(json.dumps(result.to_dict(), indent=2))


@app.command("detect-quadrature")
def detect_quadrature_cmd(
    file: Path = typer.Argument(..., help="Python file to analyze"),
    entry_function: str | None = typer.Option(None, help="Entry function name"),
) -> None:
    """Detect trapezoidal vs Simpson quadrature method."""
    result = detect_quadrature_file(str(file), entry_function=entry_function)
    typer.echo(json.dumps(result.to_dict(), indent=2))


@app.command("detect-eager-lazy")
def detect_eager_lazy_cmd(
    file: Path = typer.Argument(..., help="Python file to analyze"),
    expected: str | None = typer.Option(None, "--expected", help="eager or lazy"),
) -> None:
    """Detect eager vs lazy feature pipeline timing signature."""
    result = detect_eager_lazy_file(str(file))
    payload = result.to_dict()
    if expected is not None and payload["method"] != expected:
        typer.echo(json.dumps(payload, indent=2))
        typer.echo(
            f"Expected {expected} but detected {payload['method']}",
            err=True,
        )
        raise typer.Exit(1)
    typer.echo(json.dumps(payload, indent=2))


@app.command("detect-bfs-dfs")
def detect_bfs_dfs_cmd(
    file: Path = typer.Argument(..., help="Python file to analyze"),
    task_id: str = typer.Option(..., "--task-id", help="Task ID from bfs_dfs_tasks.json"),
) -> None:
    """Detect BFS vs DFS graph traversal order signature."""
    result = detect_bfs_dfs_file(str(file), task_id=task_id)
    typer.echo(json.dumps(result.to_dict(), indent=2))


@app.command("detect-deterministic-randomized")
def detect_deterministic_randomized_cmd(
    file: Path = typer.Argument(..., help="Python file to analyze"),
    task_id: str = typer.Option(
        ...,
        "--task-id",
        help="Task ID from deterministic_randomized_tasks.json",
    ),
    mode: str = typer.Option(
        "primary",
        "--mode",
        help="primary or fixed_seed_control",
    ),
    runs: int = typer.Option(5, "--runs", help="Repeated executions per detection"),
) -> None:
    """Detect deterministic vs randomized inter-execution variability signature."""
    if mode not in ("primary", "fixed_seed_control"):
        typer.echo("mode must be primary or fixed_seed_control", err=True)
        raise typer.Exit(1)
    result = detect_deterministic_randomized_file(
        str(file),
        task_id=task_id,
        mode=mode,  # type: ignore[arg-type]
        run_count=runs,
    )
    typer.echo(json.dumps(result.to_dict(), indent=2))


@app.command("strip")
def strip_cmd(
    file: Path = typer.Argument(..., help="Python file to strip"),
    level: StripLevel = typer.Option(
        StripLevel.RAW,
        "--level",
        help="Stripping level",
    ),
    sidecar: Path | None = typer.Option(
        None,
        "--sidecar",
        help="JSON sidecar path (lock_marker_strip evidence)",
    ),
) -> None:
    """Apply deterministic stripping transforms."""
    stripped, evidence = strip_file_with_evidence(
        str(file), level, sidecar_path=sidecar
    )
    typer.echo(stripped)
    if evidence is not None:
        sidecar_written = sidecar or (file.parent / f"{file.name}.lock_marker_strip.json")
        typer.echo(f"Wrote sidecar {sidecar_written}", err=True)


@app.command("smoke-test")
def smoke_test() -> None:
    """Run end-to-end smoke test without APIs."""
    from invert_core.tasks import fixtures_dir as fix_dir

    fix = fix_dir()
    report = verify_fixture_dir(fix)
    typer.echo(json.dumps(report, indent=2, default=str))
    if not report["passed"]:
        typer.echo("Smoke test FAILED", err=True)
        raise typer.Exit(1)
    typer.echo("Smoke test passed.")


@app.command("analyze-slice")
def analyze_slice_cmd(
    fixtures: Path | None = typer.Option(None, help="Fixtures directory"),
    output: Path | None = typer.Option(None, help="Output directory"),
) -> None:
    """Verify Core v2 slice against preregistered logic (fixtures only)."""
    fix_dir = fixtures or fixtures_dir()
    out_dir = output or results_dir()

    result = run_analyze_slice(fix_dir, out_dir)
    typer.echo(f"Wrote {result.analysis_path}")
    typer.echo(f"Wrote {result.matrix_path}")
    typer.echo(f"Wrote {result.summary_path}")
    if not result.passed:
        typer.echo("Slice analysis FAILED preregistered checks", err=True)
        raise typer.Exit(1)
    typer.echo("Slice analysis passed.")


@app.command("analyze-run")
def analyze_run_cmd(
    run: str = typer.Option(..., "--run", help="Run name"),
    config: Path | None = typer.Option(None, "--config", help="Pilot config (optional)"),
) -> None:
    """Analyze generated Core v2 run (detector + behavioral oracle)."""
    root = project_root()
    result = run_analyze_run(run, root, config_path=config)
    typer.echo(f"Wrote {result.detection_path}")
    typer.echo(f"Wrote {result.summary_path}")
    typer.echo(f"Wrote {result.valid_summary_path}")
    typer.echo(f"Wrote {result.report_path}")
    fixed_seed_path = result.stats.get("fixed_seed_control_path")
    if fixed_seed_path:
        typer.echo(f"Wrote {fixed_seed_path}")


@app.command("summarize-core-v2")
def summarize_core_v2_cmd() -> None:
    """Aggregate completed Core v2 runs into cross-run decision dashboards."""
    root = project_root()
    result = run_summarize_core_v2(root)
    typer.echo(f"Wrote {result.model_summary_path}")
    typer.echo(f"Wrote {result.dimension_summary_path}")
    typer.echo(f"Wrote {result.decision_report_path}")


@app.command("diagnose-quadrature")
def diagnose_quadrature_cmd(
    run: str = typer.Option(..., "--run", help="Core v2 quadrature run name"),
) -> None:
    """Diagnose trapezoidal detector failures for a quadrature pilot run."""
    root = project_root()
    result = run_diagnose_quadrature(run, root)
    typer.echo(f"Wrote {result.csv_path} ({len(result.rows)} rows)")
    typer.echo(f"Wrote {result.md_path}")


@app.command("diagnose-deterministic-randomized")
def diagnose_deterministic_randomized_cmd(
    run: str = typer.Option(..., "--run", help="Core v2 deterministic/randomized run name"),
) -> None:
    """Diagnose behavioral validity failures for a deterministic/randomized pilot run."""
    root = project_root()
    result = run_diagnose_deterministic_randomized(run, root)
    typer.echo(f"Wrote {result.csv_path} ({len(result.rows)} rows)")
    typer.echo(f"Wrote {result.md_path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
