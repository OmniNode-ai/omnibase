# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T11:54:46.692543'
# description: Stamped by PythonHandler
# entrypoint: python://fix_node_health
# hash: 489ef244b2618f3097000b1dc2a9a7d38132b35e4843f2bb5cdd9ace0fba4c45
# last_modified_at: '2025-05-29T14:13:58.375737+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: fix_node_health.py
# namespace: python://omnibase.cli_tools.onex.v1_0_0.commands.fix_node_health
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: b9e27103-7068-45c2-beb0-2b9d03dbf540
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
CLI command for comprehensive node health fixes.
"""

from pathlib import Path
from typing import List, Optional

import typer

from omnibase.enums import OnexStatus
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.nodes.node_manager_node.v1_0_0.helpers.helpers_maintenance import (
    NodeMaintenanceGenerator,
)


def get_result_message(result: OnexResultModel) -> str:
    """Extract message text from OnexResultModel messages."""
    if not result.messages:
        return "No message available"

    # If there's only one message, return its summary
    if len(result.messages) == 1:
        return result.messages[0].summary

    # If there are multiple messages, combine them
    return "; ".join(msg.summary for msg in result.messages)


def fix_node_health(
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
    generator = NodeMaintenanceGenerator(
        template_directory=template_directory, backup_enabled=not no_backup
    )

    # Determine which nodes to process
    if nodes:
        node_paths = [nodes_directory / node_name for node_name in nodes]
        # Validate that specified nodes exist
        for node_path in node_paths:
            if not node_path.exists():
                typer.echo(f"❌ Error: Node directory not found: {node_path}", err=True)
                return
    else:
        # Process all node directories
        node_paths = [
            path
            for path in nodes_directory.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        ]

    if not node_paths:
        typer.echo("❌ No nodes found to process")
        return

    if dry_run:
        typer.echo(
            f"🔍 DRY RUN: Would perform health fixes for {len(node_paths)} nodes"
        )
    else:
        typer.echo(f"🏥 Performing health fixes for {len(node_paths)} nodes")

    success_count = 0
    error_count = 0
    total_fixes = 0

    for node_path in sorted(node_paths):
        if verbose:
            typer.echo(f"\n📁 Processing: {node_path.name}")

        result = generator.fix_node_health(node_path, dry_run=dry_run)

        if result.status == OnexStatus.SUCCESS:
            success_count += 1
            fixes_applied = (
                result.metadata.get("fixes_applied", []) if result.metadata else []
            )
            potential_fixes = (
                result.metadata.get("potential_fixes", []) if result.metadata else []
            )

            if dry_run:
                fix_count = len(potential_fixes)
                total_fixes += fix_count
                if verbose:
                    typer.echo(
                        f"  🔍 Would apply {fix_count} fixes: {', '.join(potential_fixes)}"
                    )
            else:
                fix_count = len(fixes_applied)
                total_fixes += fix_count
                if verbose:
                    typer.echo(
                        f"  ✅ Applied {fix_count} fixes: {', '.join(fixes_applied)}"
                    )
        else:
            error_count += 1
            typer.echo(f"  ❌ {get_result_message(result)}", err=True)

    # Summary
    typer.echo(f"\n📊 Summary:")
    typer.echo(f"  ✅ Nodes processed successfully: {success_count}")
    if error_count > 0:
        typer.echo(f"  ❌ Nodes with errors: {error_count}")

    if dry_run:
        typer.echo(f"  🔍 Total potential fixes: {total_fixes}")
        typer.echo(f"\n💡 Run with --apply to make actual changes")
    else:
        typer.echo(f"  🔧 Total fixes applied: {total_fixes}")
        if total_fixes > 0 and not no_backup:
            typer.echo(f"💾 Backups created in .node_maintenance_backups/")


if __name__ == "__main__":
    typer.run(fix_node_health)
