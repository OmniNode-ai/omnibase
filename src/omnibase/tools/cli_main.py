# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: cli_main.py
# version: 1.0.0
# uuid: 753581a3-5600-4e60-a622-d3b5c21913bc
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.168780
# last_modified_at: 2025-05-21T16:42:46.079751
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 4bd53e6134847b022a536e4a9a6847b42e8e2390bbe1480c611a2169719b470c
# entrypoint: {'type': 'python', 'target': 'cli_main.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.cli_main
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
