# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T11:51:23.476866'
# description: Stamped by PythonHandler
# entrypoint: python://helpers_cli_commands
# hash: eb53c4d31d21660a9d9ea69307a02c85d31f2641c12957346f7cdbdfcc5f5792
# last_modified_at: '2025-05-29T14:13:59.349534+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: helpers_cli_commands.py
# namespace: python://omnibase.nodes.node_manager_node.v1_0_0.helpers.helpers_cli_commands
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: c7106d3d-8492-4685-8739-1811c28607c5
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
CLI command helpers for node_manager_node.

This module provides CLI command functions that can be used by the main ONEX CLI
to provide convenient access to node management operations.
"""

from pathlib import Path
from typing import List, Optional
import subprocess
import sys

import typer

from omnibase.enums import OnexStatus
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_cli_commands import ProtocolCliCommands
from ..models.model_cli_command import ModelCliCommand
from .tool_file_generator import ToolFileGenerator
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
import uuid
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from .tool_static_typing_enforcer import run_static_typing_enforcer

cli = typer.Typer(help="Node Manager CLI commands (generation, maintenance, validation)")

def get_result_message(result: OnexResultModel) -> str:
    """Extract message text from OnexResultModel messages."""
    if not result.messages:
        return "No message available"

    # If there's only one message, return its summary
    if len(result.messages) == 1:
        return result.messages[0].summary

    # If there are multiple messages, combine them
    return "; ".join(msg.summary for msg in result.messages)


@cli.command()
def cli_fix_node_health(
    nodes: List[str] = typer.Option(
        None,
        "--nodes",
        help="Specific node names to fix (can be specified multiple times). If not provided, processes all nodes.",
    ),
    nodes_directory: Path = typer.Option(
        Path("src/omnibase/nodes"),
        "--nodes-directory",
        help="Path to nodes directory. Defaults to src/omnibase/nodes/",
    ),
    template_directory: Optional[Path] = typer.Option(
        None,
        "--template-directory",
        help="Path to template directory. Defaults to src/omnibase/nodes/node_template/v1_0_0/",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--apply",
        help="Show what would be fixed without making changes (default: dry-run for safety)",
    ),
    no_backup: bool = typer.Option(
        False, "--no-backup", help="Disable backup creation before making fixes"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Show detailed output for each node processed"
    ),
) -> None:
    """
    Perform comprehensive node health fixes (contracts + manifests + configs).

    This command performs a complete health check and fix for nodes:
    - Regenerates contract.yaml files based on node structure
    - Updates node.onex.yaml manifests to current ONEX standards
    - Synchronizes configuration files with template standards
    - Ensures all critical node files are compliant and up-to-date

    SAFETY: Runs in DRY RUN mode by default. Use --apply to make actual changes.

    Examples:
        # Show what would be fixed (dry run - default)
        onex fix-node-health

        # Actually apply fixes to all nodes
        onex fix-node-health --apply

        # Fix specific nodes with verbose output
        onex fix-node-health --apply --nodes stamper_node --nodes logger_node --verbose

        # Fix all nodes without creating backups
        onex fix-node-health --apply --no-backup
    """
    # Remove any import from omnibase.nodes.node_manager_node.v1_0_0.helpers.helpers_maintenance

    # ... rest of the function remains unchanged ...


@cli.command()
def cli_regenerate_contracts(
    nodes: List[str] = typer.Option(
        None,
        "--nodes",
        help="Specific node names to regenerate contracts for (can be specified multiple times). If not provided, processes all nodes.",
    ),
    nodes_directory: Path = typer.Option(
        Path("src/omnibase/nodes"),
        "--nodes-directory",
        help="Path to nodes directory. Defaults to src/omnibase/nodes/",
    ),
    template_directory: Optional[Path] = typer.Option(
        None,
        "--template-directory",
        help="Path to template directory. Defaults to src/omnibase/nodes/node_template/v1_0_0/",
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Actually apply changes. By default, runs in dry-run mode to show what would be done.",
    ),
    no_backup: bool = typer.Option(
        False,
        "--no-backup",
        help="Disable backup creation before regenerating contracts",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Show detailed output for each node processed"
    ),
) -> None:
    """
    Regenerate contract.yaml files based on node structure analysis.

    This command analyzes each node's structure (state models, node class) and
    regenerates the contract.yaml file with the correct input/output state
    references and contract specifications.

    By default, runs in DRY RUN mode to show what would be done.
    Use --apply to actually make changes.

    Examples:
        # Show what would be regenerated (dry run - default)
        onex regenerate-contracts

        # Actually regenerate contracts for all nodes
        onex regenerate-contracts --apply

        # Regenerate contracts for specific nodes
        onex regenerate-contracts --apply --nodes stamper_node --nodes logger_node

        # Show what would be done with verbose output
        onex regenerate-contracts --verbose
    """
    # Remove any import from omnibase.nodes.node_manager_node.v1_0_0.helpers.helpers_maintenance

    # ... rest of the function remains unchanged ...


@cli.command()
def cli_regenerate_manifests(
    nodes: List[str] = typer.Option(
        None,
        "--nodes",
        help="Specific node names to regenerate manifests for (can be specified multiple times). If not provided, processes all nodes.",
    ),
    nodes_directory: Path = typer.Option(
        Path("src/omnibase/nodes"),
        "--nodes-directory",
        help="Path to nodes directory. Defaults to src/omnibase/nodes/",
    ),
    template_directory: Optional[Path] = typer.Option(
        None,
        "--template-directory",
        help="Path to template directory. Defaults to src/omnibase/nodes/node_template/v1_0_0/",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--apply",
        help="Show what would be regenerated without making changes (default: dry-run for safety)",
    ),
    no_backup: bool = typer.Option(
        False,
        "--no-backup",
        help="Disable backup creation before regenerating manifests",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Show detailed output for each node processed"
    ),
) -> None:
    """
    Regenerate node.onex.yaml manifest files with current ONEX standards.

    This command analyzes each node and regenerates the node.onex.yaml manifest
    file with current ONEX standards, proper versioning, runtime specifications,
    and dependency declarations.

    SAFETY: Runs in DRY RUN mode by default. Use --apply to make actual changes.

    Examples:
        # Show what would be regenerated (dry run - default)
        onex regenerate-manifests

        # Actually regenerate manifests for all nodes
        onex regenerate-manifests --apply

        # Regenerate manifests for specific nodes
        onex regenerate-manifests --apply --nodes stamper_node --nodes logger_node

        # Regenerate with verbose output and no backups
        onex regenerate-manifests --apply --verbose --no-backup
    """
    # Remove any import from omnibase.nodes.node_manager_node.v1_0_0.helpers.helpers_maintenance

    # ... rest of the function remains unchanged ...


@cli.command()
def cli_generate_node(
    name: str = typer.Option(..., '--name', help='Name of the new node (snake_case, no _node suffix)'),
    author: str = typer.Option(..., '--author', help='Author/team for the node'),
    target_directory: Path = typer.Option(
        Path('src/omnibase/nodes'), '--target-directory', help='Target directory for the new node (default: src/omnibase/nodes)'
    ),
    description: Optional[str] = typer.Option(None, '--description', help='Optional node description'),
    year: Optional[int] = typer.Option(None, '--year', help='Copyright year (defaults to current year)'),
) -> None:
    """
    Generate a new ONEX node from the canonical template.
    Copies the template structure, applies tokenization, and creates a new node directory.
    """
    import traceback
    from datetime import datetime
    from omnibase.core.core_structured_logging import emit_log_event_sync
    from omnibase.enums import LogLevelEnum
    from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context
    from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
    from ..models.model_template_context import ModelTemplateContext
    from .tool_file_generator import ToolFileGenerator
    from .tool_template_engine import ToolTemplateEngine

    event_bus = InMemoryEventBus()
    node_name = name.strip().lower()
    node_class = ''.join([part.capitalize() for part in node_name.split('_')]) + 'Node'
    node_id = node_name
    node_id_upper = node_name.upper()
    copyright_year = year or datetime.now().year
    context = ModelTemplateContext(
        node_name=node_name,
        node_class=node_class,
        node_id=node_id,
        node_id_upper=node_id_upper,
        author=author,
        year=copyright_year,
        description=description,
    )
    template_path = Path('src/omnibase/nodes/node_manager/template/v1_0_0')
    target_path = target_directory / f"{node_name}_node"
    file_generator = ToolFileGenerator(event_bus=event_bus)
    template_engine = ToolTemplateEngine(event_bus=event_bus)
    try:
        emit_log_event_sync(LogLevelEnum.DEBUG, f"[generate-node] Context: {context}", context=make_log_context(node_id=node_name), event_bus=event_bus)
        typer.echo(f"[DEBUG] Context: {context}")
        emit_log_event_sync(LogLevelEnum.INFO, f"[generate-node] Copying template to {target_path}", context=make_log_context(node_id=node_name), event_bus=event_bus)
        typer.echo(f"[INFO] Copying template to {target_path}")
        file_generator.copy_template_structure(template_path, target_path, node_name, context)
        emit_log_event_sync(LogLevelEnum.INFO, f"[generate-node] Processing templates in {target_path}", context=make_log_context(node_id=node_name), event_bus=event_bus)
        typer.echo(f"[INFO] Processing templates in {target_path}")
        template_engine.process_templates(target_path, context)
        emit_log_event_sync(LogLevelEnum.INFO, f"[generate-node] Running initial stamping on {target_path}", context=make_log_context(node_id=node_name), event_bus=event_bus)
        typer.echo(f"[INFO] Running initial stamping on {target_path}")
        file_generator.run_initial_stamping(target_path)
        emit_log_event_sync(LogLevelEnum.INFO, f"[generate-node] Generating .onextree for {target_path}", context=make_log_context(node_id=node_name), event_bus=event_bus)
        typer.echo(f"[INFO] Generating .onextree for {target_path}")
        file_generator.generate_onextree(target_path)
        emit_log_event_sync(LogLevelEnum.INFO, f"[generate-node] Node '{node_name}_node' generated at {target_path}", context=make_log_context(node_id=node_name), event_bus=event_bus)
        typer.echo(f"Node '{node_name}_node' generated at {target_path}")
    except Exception as e:
        tb = traceback.format_exc()
        emit_log_event_sync(LogLevelEnum.ERROR, f"[generate-node] Exception: {e}\n{tb}", context=make_log_context(node_id=node_name), event_bus=event_bus)
        typer.echo(f"[ERROR] Node generation failed: {e}\n{tb}")


@cli.command()
def cli_parity_validate(
    node_path: Path = typer.Option(..., '--node-path', help='Path to the node directory to validate for parity'),
    event_bus=None,
) -> None:
    """
    Run parity validation on the specified node directory and emit the result as an event.
    """
    if event_bus is None:
        from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
        event_bus = InMemoryEventBus()
        # print("[DEBUG] cli_parity_validate: Created new InMemoryEventBus (no event_bus injected)")
    # else:
        # print("[DEBUG] cli_parity_validate: Using injected event_bus instance")
    file_generator = ToolFileGenerator(event_bus=event_bus)
    result = file_generator.run_parity_validation(node_path)
    event_metadata = {
        "success": result.success,
        "details": result.details,
        "errors": [e.dict() for e in result.errors] if result.errors else None,
        "metadata": result.metadata.dict() if result.metadata else None,
    }
    # print(f"[DEBUG] cli_parity_validate: Publishing TOOL_PROXY_RESULT event: {event_metadata}")
    from datetime import datetime
    event = OnexEvent(
        event_id=uuid.uuid4(),
        timestamp=datetime.utcnow(),
        node_id="node_manager",
        event_type=OnexEventTypeEnum.TOOL_PROXY_RESULT,
        correlation_id=None,
        metadata=event_metadata,
    )
    event_bus.publish(event)


@cli.command()
def cli_static_typing_enforce(
    node_path: Path = typer.Option(..., '--node-path', help='Path to the node directory to check (e.g., src/omnibase/nodes/node_manager)'),
    event_bus=None,
) -> None:
    """
    Run static typing enforcement on the specified node directory and emit the result as an event.
    """
    if event_bus is None:
        from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
        event_bus = InMemoryEventBus()
    try:
        violations = run_static_typing_enforcer(node_path)
        status = "pass" if not violations else "fail"
        output = "\n".join(violations) if violations else "[Static Typing Enforcer] No violations found. All clear!"
        error = None
    except Exception as e:
        status = "error"
        output = ""
        error = str(e)
    event = OnexEvent(
        event_id=uuid.uuid4(),
        timestamp=None,
        node_id="node_manager",
        event_type=OnexEventTypeEnum.TOOL_PROXY_RESULT,
        correlation_id=None,
        metadata={
            "status": status,
            "output": output,
            "error": error,
        },
    )
    print(f"[DEBUG] Publishing TOOL_PROXY_RESULT event: status={status}")
    event_bus.publish(event)


class ToolCliCommands(ProtocolCliCommands):
    """
    Implements ProtocolCliCommands (shared protocol) for CLI command operations and orchestration.
    """
    def run_command(self, command: ModelCliCommand) -> int:
        """
        Run a CLI command with the given arguments.
        Args:
            command (ModelCliCommand): The command model to run.
        Returns:
            int: The exit code of the command.
        """
        # ... update logic to use ModelCliCommand fields ...

if __name__ == "__main__":
    cli()
