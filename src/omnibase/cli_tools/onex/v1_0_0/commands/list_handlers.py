# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: list_handlers.py
# version: 1.0.0
# uuid: 1e53f862-d595-4858-b28d-f5f4c9110362
# author: OmniNode Team
# created_at: 2025-05-25T12:33:57.407212
# last_modified_at: 2025-05-25T16:51:44.604062
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 3f26c2cffc210ebe70488cec7b63c50e1ecbeb7d1c4c877dc71f641505426de7
# entrypoint: python@list_handlers.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.list_handlers
# meta_type: tool
# === /OmniNode:Metadata ===


"""
CLI command to list all registered handlers and plugins.

This module provides the `onex handlers list` command that displays comprehensive
information about all registered file type handlers, including their source,
priority, supported file types, and metadata.
"""

import json
from typing import Any, Dict, List, Optional

import typer

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry

app = typer.Typer(
    name="handlers",
    help="Commands for managing and inspecting file type handlers and plugins.",
)


def format_extensions_list(extensions: List[str]) -> str:
    """Format a list of extensions for display."""
    if not extensions:
        return "None"
    return ", ".join(sorted(extensions))


def format_filenames_list(filenames: List[str]) -> str:
    """Format a list of filenames for display."""
    if not filenames:
        return "None"
    return ", ".join(sorted(filenames))


@app.command("list")
def list_handlers(
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, or summary"
    ),
    source_filter: Optional[str] = typer.Option(
        None,
        "--source",
        "-s",
        help="Filter by source: core, runtime, node-local, plugin",
    ),
    type_filter: Optional[str] = typer.Option(
        None, "--type", "-t", help="Filter by type: extension, special, named"
    ),
    show_metadata: bool = typer.Option(
        False, "--metadata", "-m", help="Show detailed handler metadata"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show verbose output with all details"
    ),
) -> None:
    """
    List all registered file type handlers and plugins.

    Shows comprehensive information about handlers including their source
    (core/runtime/node-local/plugin), priority, supported file types, and metadata.
    """
    # Create registry and load all handlers
    registry = FileTypeHandlerRegistry()
    registry.register_all_handlers()

    # Get all handlers
    handlers = registry.list_handlers()

    # Apply filters
    filtered_handlers = {}
    for handler_id, handler_info in handlers.items():
        # Apply source filter
        if source_filter and handler_info.get("source") != source_filter:
            continue

        # Apply type filter
        if type_filter and handler_info.get("type") != type_filter:
            continue

        filtered_handlers[handler_id] = handler_info

    if not filtered_handlers:
        print("No handlers found matching the specified filters.")
        return

    # Output based on format
    if format_type == "json":
        print(json.dumps(filtered_handlers, indent=2, default=str))
    elif format_type == "summary":
        _print_summary(filtered_handlers)
    else:  # table format (default)
        _print_table(filtered_handlers, show_metadata, verbose)


def _print_summary(handlers: Dict[str, Dict[str, Any]]) -> None:
    """Print a summary of handlers by source and type."""
    # Count by source
    source_counts: Dict[str, int] = {}
    type_counts: Dict[str, int] = {}

    for handler_info in handlers.values():
        source = handler_info.get("source", "unknown")
        handler_type = handler_info.get("type", "unknown")

        source_counts[source] = source_counts.get(source, 0) + 1
        type_counts[handler_type] = type_counts.get(handler_type, 0) + 1

    print("\nHandler Summary")
    print("=" * 50)

    print(f"\nTotal Handlers: {len(handlers)}")

    print("\nBy Source:")
    for source, count in sorted(source_counts.items()):
        print(f"  {source}: {count}")

    print("\nBy Type:")
    for handler_type, count in sorted(type_counts.items()):
        print(f"  {handler_type}: {count}")


def _print_table(
    handlers: Dict[str, Dict[str, Any]], show_metadata: bool, verbose: bool
) -> None:
    """Print handlers in a formatted table."""
    if verbose:
        show_metadata = True

    print("\nRegistered File Type Handlers")
    print("=" * 80)

    # Define column widths
    col_widths = {
        "id": 25,
        "type": 10,
        "key": 15,
        "class": 20,
        "source": 12,
        "priority": 8,
        "name": 20,
        "version": 10,
        "author": 15,
        "description": 30,
        "extensions": 20,
        "files": 20,
        "content": 8,
    }

    # Build header
    header_parts = [
        "Handler ID".ljust(col_widths["id"]),
        "Type".ljust(col_widths["type"]),
        "Key".ljust(col_widths["key"]),
        "Class".ljust(col_widths["class"]),
        "Source".ljust(col_widths["source"]),
        "Priority".ljust(col_widths["priority"]),
    ]

    if show_metadata:
        header_parts.extend(
            [
                "Name".ljust(col_widths["name"]),
                "Version".ljust(col_widths["version"]),
                "Author".ljust(col_widths["author"]),
                "Description".ljust(col_widths["description"]),
            ]
        )

    if verbose:
        header_parts.extend(
            [
                "Supported Ext".ljust(col_widths["extensions"]),
                "Supported Files".ljust(col_widths["files"]),
                "Content".ljust(col_widths["content"]),
            ]
        )

    print(" | ".join(header_parts))
    print("-" * (sum(col_widths.values()) + len(header_parts) * 3))

    # Print rows
    for handler_id, handler_info in sorted(handlers.items()):
        # Basic columns
        row_parts = [
            handler_id[: col_widths["id"]].ljust(col_widths["id"]),
            handler_info.get("type", "unknown")[: col_widths["type"]].ljust(
                col_widths["type"]
            ),
            handler_info.get("key", "")[: col_widths["key"]].ljust(col_widths["key"]),
            handler_info.get("handler_class", "")[: col_widths["class"]].ljust(
                col_widths["class"]
            ),
            handler_info.get("source", "unknown")[: col_widths["source"]].ljust(
                col_widths["source"]
            ),
            str(handler_info.get("priority", 0))[: col_widths["priority"]].ljust(
                col_widths["priority"]
            ),
        ]

        if show_metadata:
            # Metadata columns
            row_parts.extend(
                [
                    handler_info.get("handler_name", "N/A")[: col_widths["name"]].ljust(
                        col_widths["name"]
                    ),
                    handler_info.get("handler_version", "N/A")[
                        : col_widths["version"]
                    ].ljust(col_widths["version"]),
                    handler_info.get("handler_author", "N/A")[
                        : col_widths["author"]
                    ].ljust(col_widths["author"]),
                    (
                        handler_info.get("handler_description", "N/A")[
                            : col_widths["description"]
                        ]
                    ).ljust(col_widths["description"]),
                ]
            )

        if verbose:
            # Verbose columns
            supported_ext = handler_info.get("supported_extensions", [])
            supported_files = handler_info.get("supported_filenames", [])
            content_analysis = handler_info.get("requires_content_analysis", False)

            row_parts.extend(
                [
                    format_extensions_list(supported_ext)[
                        : col_widths["extensions"]
                    ].ljust(col_widths["extensions"]),
                    format_filenames_list(supported_files)[: col_widths["files"]].ljust(
                        col_widths["files"]
                    ),
                    ("Yes" if content_analysis else "No")[
                        : col_widths["content"]
                    ].ljust(col_widths["content"]),
                ]
            )

        print(" | ".join(row_parts))

    # Print additional info
    print(f"\nTotal: {len(handlers)} handlers")

    # Show priority legend
    print("\nPriority Legend:")
    print("  100+: Core handlers (essential system functionality)")
    print("  50-99: Runtime handlers (standard ONEX ecosystem)")
    print("  10-49: Node-local handlers (node-specific functionality)")
    print("  0-9: Plugin handlers (third-party or experimental)")


if __name__ == "__main__":
    app()
