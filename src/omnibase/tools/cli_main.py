# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 988210ae-8327-4435-b59d-c4c9e4c65cb5
# name: cli_main.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:01.700617
# last_modified_at: 2025-05-19T16:20:01.700618
# description: Stamped Python file: cli_main.py
# state_contract: none
# lifecycle: active
# hash: 6fefc18036064aa788077ebb36379c6cec5f3bba6372a4b7f101a358cb9fc5d8
# entrypoint: {'type': 'python', 'target': 'cli_main.py'}
# namespace: onex.stamped.cli_main.py
# meta_type: tool
# === /OmniNode:Metadata ===

import logging
import sys

import typer

from omnibase.tools.cli_stamp import app as stamp_app

# Import CLI tools
from omnibase.tools.cli_validate import app as validate_app

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("onex")

# Create the main CLI app
app = typer.Typer(
    name="onex",
    help="ONEX CLI tool for node validation, stamping, and execution.",
    add_completion=True,
)

# Add subcommands
app.add_typer(validate_app, name="validate")
app.add_typer(stamp_app, name="stamp")


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Silence all output except errors"
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
) -> None:
    """
    ONEX: Open Node Execution - Command Line Interface

    Validate, stamp, and execute ONEX nodes.
    """
    # Configure logging
    log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.DEBUG
    elif quiet:
        log_level = logging.ERROR

    logging.getLogger().setLevel(log_level)
    logger.debug("Debug logging enabled")


@app.command()
def version() -> None:
    """
    Display version information.
    """
    typer.echo("ONEX CLI v0.1.0")
    typer.echo("Part of OmniBase Milestone 0")


@app.command()
def info() -> None:
    """
    Display system information.
    """
    typer.echo("ONEX CLI System Information")
    typer.echo("---------------------------")
    typer.echo(f"Python version: {sys.version}")
    typer.echo(f"Platform: {sys.platform}")
    typer.echo("Loaded modules:")
    modules = [
        "omnibase",
        "omnibase.core",
        "omnibase.protocol",
        "omnibase.schema",
        "omnibase.tools",
    ]
    for module in modules:
        try:
            __import__(module)
            typer.echo(f"  ✓ {module}")
        except ImportError:
            typer.echo(f"  ✗ {module}")


if __name__ == "__main__":
    app()
