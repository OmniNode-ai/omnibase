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
        help="Path to template directory. Defaults to src/omnibase/nodes/template_node/v1_0_0/",
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
        help="Path to template directory. Defaults to src/omnibase/nodes/template_node/v1_0_0/",
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

    # Dry run is the default (apply=False means dry run)
    dry_run = not apply

    if dry_run:
        typer.echo(
            f"🔍 DRY RUN: Would regenerate contracts for {len(node_paths)} nodes"
        )
    else:
        typer.echo(f"🔄 Regenerating contracts for {len(node_paths)} nodes")

    success_count = 0
    error_count = 0

    for node_path in sorted(node_paths):
        if verbose:
            typer.echo(f"\n📁 Processing: {node_path.name}")

        result = generator.regenerate_contract(node_path, dry_run=dry_run)

        if result.status == OnexStatus.SUCCESS:
            success_count += 1
            if verbose or dry_run:
                typer.echo(f"  ✅ {get_result_message(result)}")
        else:
            error_count += 1
            typer.echo(f"  ❌ {get_result_message(result)}", err=True)

    # Summary
    typer.echo(f"\n📊 Summary:")
    typer.echo(f"  ✅ Success: {success_count}")
    if error_count > 0:
        typer.echo(f"  ❌ Errors: {error_count}")

    if dry_run:
        typer.echo(f"\n💡 Add --apply to actually make changes")
    elif success_count > 0 and not no_backup:
        typer.echo(f"💾 Backups created in .node_maintenance_backups/")


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
        help="Path to template directory. Defaults to src/omnibase/nodes/template_node/v1_0_0/",
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
            f"🔍 DRY RUN: Would regenerate manifests for {len(node_paths)} nodes"
        )
    else:
        typer.echo(f"🔄 Regenerating manifests for {len(node_paths)} nodes")

    success_count = 0
    error_count = 0

    for node_path in sorted(node_paths):
        if verbose:
            typer.echo(f"\n📁 Processing: {node_path.name}")

        result = generator.regenerate_manifest(node_path, dry_run=dry_run)

        if result.status == OnexStatus.SUCCESS:
            success_count += 1
            if verbose or dry_run:
                typer.echo(f"  ✅ {get_result_message(result)}")
        else:
            error_count += 1
            typer.echo(f"  ❌ {get_result_message(result)}", err=True)

    # Summary
    typer.echo(f"\n📊 Summary:")
    typer.echo(f"  ✅ Success: {success_count}")
    if error_count > 0:
        typer.echo(f"  ❌ Errors: {error_count}")

    if dry_run:
        typer.echo(f"\n💡 Run with --apply to make actual changes")
    elif success_count > 0 and not no_backup:
        typer.echo(f"💾 Backups created in .node_maintenance_backups/")
