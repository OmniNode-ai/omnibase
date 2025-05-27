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
# entrypoint: python@cli_main.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.cli_main
# meta_type: tool
# === /OmniNode:Metadata ===


import json
import sys
from pathlib import Path

import typer

from omnibase.cli_tools.onex.v1_0_0.commands.list_handlers import app as handlers_app
from omnibase.core.core_structured_logging import (
    emit_log_event,
    setup_structured_logging,
)
from omnibase.enums import LogLevelEnum
from omnibase.nodes.registry import NODE_CLI_REGISTRY

from .cli_version_resolver import global_resolver

# CLI tools imports removed - validation now handled by parity_validator_node and stamper_node

# Setup structured logging (replaces traditional logging)
setup_structured_logging()

# Component identifier for logging - derived from module name
_COMPONENT_NAME = Path(__file__).stem

# Create the main CLI app
app = typer.Typer(
    name="onex",
    help="ONEX CLI tool for node validation, stamping, and execution.",
    add_completion=True,
)

# Add subcommands
# Note: validate command removed - use 'onex run parity_validator_node' instead
stamp_app = NODE_CLI_REGISTRY["stamper_node@v1_0_0"]
app.add_typer(stamp_app, name="stamp")
app.add_typer(handlers_app, name="handlers")


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
    # Configure structured logging level
    if debug:
        log_level = LogLevelEnum.DEBUG
    elif verbose:
        log_level = LogLevelEnum.DEBUG
    elif quiet:
        log_level = LogLevelEnum.ERROR
    else:
        log_level = LogLevelEnum.INFO

    # Update global logging configuration
    from omnibase.core.core_structured_logging import get_global_config

    config = get_global_config()
    if config:
        config.log_level = log_level

    if debug:
        emit_log_event(
            LogLevelEnum.DEBUG, "Debug logging enabled", node_id=_COMPONENT_NAME
        )


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


@app.command()
def run(
    node_name: str = typer.Argument(..., help="Name of the node to run"),
    version: str = typer.Option(
        None, "--version", help="Specific version to run (defaults to latest)"
    ),
    list_versions: bool = typer.Option(
        False, "--list-versions", help="List available versions for the specified node"
    ),
    introspect: bool = typer.Option(
        False, "--introspect", help="Show node introspection information"
    ),
    node_args: str = typer.Option(
        None, "--args", help="Additional arguments to pass to the node (as JSON string)"
    ),
) -> None:
    """
    Run an ONEX node with automatic version resolution.

    Examples:
      onex run parity_validator_node --args='["--format", "summary"]'
      onex run stamper_node --version v1_0_0 --args='["file", "README.md"]'
      onex run parity_validator_node --introspect
    """
    import importlib

    # Handle list-versions request
    if list_versions:
        versions = global_resolver.discover_node_versions(node_name)

        if not versions:
            typer.echo(f"❌ No versions found for node '{node_name}'", err=True)
            raise typer.Exit(1)

        latest = global_resolver.get_latest_version(node_name)

        typer.echo(f"📦 Available versions for {node_name}:")
        for version_str in versions:
            marker = " (latest)" if version_str == latest else ""
            typer.echo(f"  • {version_str}{marker}")
        return

    # Resolve version
    resolved_version = global_resolver.resolve_version(node_name, version)
    if not resolved_version:
        if version:
            typer.echo(
                f"❌ Version '{version}' not found for node '{node_name}'", err=True
            )
        else:
            typer.echo(f"❌ No versions found for node '{node_name}'", err=True)
        raise typer.Exit(1)

    # Get module path
    module_path = global_resolver.get_module_path(node_name, resolved_version)
    if not module_path:
        typer.echo(
            f"❌ Could not resolve module path for {node_name}@{resolved_version}",
            err=True,
        )
        raise typer.Exit(1)

    # Ensure module_path is not None for type checker
    assert module_path is not None

    typer.echo(f"🚀 Running {node_name}@{resolved_version}")

    try:
        # Import and run the node
        module = importlib.import_module(module_path)

        # Handle introspection request
        if introspect:
            if hasattr(module, "get_introspection"):
                introspection = module.get_introspection()
                typer.echo(json.dumps(introspection, indent=2))
                return
            else:
                typer.echo(
                    f"❌ Node {node_name} does not support introspection", err=True
                )
                raise typer.Exit(1)

        # Parse node arguments
        parsed_args = []
        if node_args:
            try:
                parsed_args = json.loads(node_args)
                if not isinstance(parsed_args, list):
                    typer.echo("❌ Node arguments must be a JSON array", err=True)
                    raise typer.Exit(1)
            except json.JSONDecodeError as e:
                typer.echo(f"❌ Invalid JSON in node arguments: {e}", err=True)
                raise typer.Exit(1)

        # Run the node's main function with arguments
        if hasattr(module, "main"):
            # Prepare arguments for the node
            node_argv = [f"{node_name}@{resolved_version}"] + parsed_args

            # Temporarily replace sys.argv for the node
            original_argv = sys.argv
            try:
                sys.argv = node_argv
                result = module.main()

                # Handle different return types
                if result is None:
                    # No return value means success
                    return
                elif isinstance(result, int):
                    # Integer exit code
                    if result != 0:
                        raise typer.Exit(result)
                else:
                    # Assume it's a Pydantic model or other object
                    # Check if it has a status field indicating success/failure
                    if hasattr(result, "status"):
                        from omnibase.enums import OnexStatus

                        if result.status == OnexStatus.SUCCESS:
                            return  # Success
                        else:
                            typer.echo(
                                f"❌ Node execution failed with status: {result.status}",
                                err=True,
                            )
                            raise typer.Exit(1)
                    else:
                        # Unknown return type, assume success if we got here
                        return

            finally:
                sys.argv = original_argv
        else:
            typer.echo(f"❌ Node {node_name} does not have a main() function", err=True)
            raise typer.Exit(1)

    except ImportError as e:
        typer.echo(f"❌ Failed to import node {node_name}: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error running node {node_name}: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def list_nodes() -> None:
    """
    List all available ONEX nodes and their versions.
    """
    all_nodes = global_resolver.discover_all_nodes()

    if not all_nodes:
        typer.echo("❌ No ONEX nodes found", err=True)
        raise typer.Exit(1)

    typer.echo("📦 Available ONEX nodes:")
    for node_name, versions in all_nodes.items():
        latest = versions[-1] if versions else "none"
        version_count = len(versions)
        typer.echo(
            f"  • {node_name} ({version_count} version{'s' if version_count != 1 else ''}, latest: {latest})"
        )


@app.command()
def node_info(
    node_name: str = typer.Argument(..., help="Name of the node to get info for"),
    version: str = typer.Option(
        None, "--version", help="Specific version (defaults to latest)"
    ),
) -> None:
    """
    Get detailed information about a specific ONEX node.
    """
    version_info = global_resolver.get_version_info(node_name)

    if not version_info["available_versions"]:
        typer.echo(f"❌ Node '{node_name}' not found", err=True)
        raise typer.Exit(1)

    typer.echo(f"📋 Node Information: {node_name}")
    typer.echo(f"   Latest Version: {version_info['latest_version']}")
    typer.echo(f"   Total Versions: {version_info['total_versions']}")
    typer.echo(f"   Module Path: {version_info['module_path_latest']}")
    typer.echo("   Available Versions:")

    for v in version_info["available_versions"]:
        status = version_info["version_status"][v]
        typer.echo(f"     • {v} ({status})")

    # Try to get introspection if available
    resolved_version = global_resolver.resolve_version(node_name, version)
    if resolved_version:
        module_path = global_resolver.get_module_path(node_name, resolved_version)
        if module_path:  # Add None check
            try:
                import importlib

                module = importlib.import_module(module_path)
                if hasattr(module, "get_introspection"):
                    introspection = module.get_introspection()
                    node_metadata = introspection.get("node_metadata", {})
                    typer.echo(
                        f"   Description: {node_metadata.get('description', 'N/A')}"
                    )
                    typer.echo(f"   Author: {node_metadata.get('author', 'N/A')}")

                    contract = introspection.get("contract", {})
                    cli_interface = contract.get("cli_interface", {})
                    if cli_interface.get("supports_introspect"):
                        typer.echo("   Supports Introspection: ✅")
                    else:
                        typer.echo("   Supports Introspection: ❌")
            except Exception:
                pass  # Silently ignore introspection errors


if __name__ == "__main__":
    app()
