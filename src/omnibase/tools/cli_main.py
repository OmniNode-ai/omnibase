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
):
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
def version():
    """
    Display version information.
    """
    typer.echo("ONEX CLI v0.1.0")
    typer.echo("Part of OmniBase Milestone 0")


@app.command()
def info():
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
