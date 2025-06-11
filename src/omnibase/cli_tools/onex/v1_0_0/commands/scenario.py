import typer
import subprocess
from pathlib import Path

app = typer.Typer(
    name="scenario",
    help="Run ONEX scenario-driven tests and manage scenario snapshots."
)

@app.command()
def run(
    scenario: Path = typer.Argument(..., help="Path to scenario chain YAML file."),
    update_snapshots: bool = typer.Option(False, "--update-snapshots", help="Update scenario snapshots with current output."),
):
    """
    Run a scenario chain YAML and (optionally) update scenario snapshots.
    """
    cmd = ["python", "tools/run_scenario.py", str(scenario)]
    if update_snapshots:
        cmd.append("--update-snapshots")  # For future extension
    typer.echo(f"[ONEX] Running scenario: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    raise typer.Exit(result.returncode) 