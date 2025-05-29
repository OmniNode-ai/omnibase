# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.386021'
# description: Stamped by PythonHandler
# entrypoint: python://list_handlers
# hash: fa1841f8d181b5479785d695954293c3a45272aef504774b60afc0226fc7f0d2
# last_modified_at: '2025-05-29T14:13:58.383006+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: list_handlers.py
# namespace: python://omnibase.cli_tools.onex.v1_0_0.commands.list_handlers
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: ff84e027-9f57-4cff-af2b-44469693347b
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
CLI command to list all registered handlers and plugins.

This module provides the `onex handlers list` command that displays comprehensive
information about all registered file type handlers, including their source,
priority, supported file types, and metadata.
"""

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum

# Component identifier for logging - derived from module name
_COMPONENT_NAME = Path(__file__).stem

app = typer.Typer(
    name="handlers",
    help="Commands for managing and inspecting file type handlers and plugins.",
)


@contextmanager
def suppress_debug_logging() -> Any:
    """Context manager to temporarily suppress debug logging during JSON output."""
    import io
    from contextlib import redirect_stderr, redirect_stdout

    # Capture both stdout and stderr to suppress all logging output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        yield


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

    # For JSON output, suppress debug logging during registration to avoid polluting output
    if format_type == "json":
        with suppress_debug_logging():
            registry.register_all_handlers()
            handlers = registry.list_handlers()
    else:
        registry.register_all_handlers()
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
        emit_log_event(
            LogLevelEnum.INFO,
            "No handlers found matching the specified filters.",
            node_id=_COMPONENT_NAME,
        )
        return

    # Output based on format
    if format_type == "json":
        # For JSON format, print directly to stdout to avoid structured logging wrapper
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

    emit_log_event(LogLevelEnum.INFO, "\nHandler Summary", node_id=_COMPONENT_NAME)
    emit_log_event(LogLevelEnum.INFO, "=" * 50, node_id=_COMPONENT_NAME)

    emit_log_event(
        LogLevelEnum.INFO, f"\nTotal Handlers: {len(handlers)}", node_id=_COMPONENT_NAME
    )

    emit_log_event(LogLevelEnum.INFO, "\nBy Source:", node_id=_COMPONENT_NAME)
    for source, count in sorted(source_counts.items()):
        emit_log_event(
            LogLevelEnum.INFO, f"  {source}: {count}", node_id=_COMPONENT_NAME
        )

    emit_log_event(LogLevelEnum.INFO, "\nBy Type:", node_id=_COMPONENT_NAME)
    for handler_type, count in sorted(type_counts.items()):
        emit_log_event(
            LogLevelEnum.INFO, f"  {handler_type}: {count}", node_id=_COMPONENT_NAME
        )


def _print_table(
    handlers: Dict[str, Dict[str, Any]], show_metadata: bool, verbose: bool
) -> None:
    """Print handlers in a formatted table."""
    if verbose:
        show_metadata = True

    emit_log_event(
        LogLevelEnum.INFO, "\nRegistered File Type Handlers", node_id=_COMPONENT_NAME
    )
    emit_log_event(LogLevelEnum.INFO, "=" * 80, node_id=_COMPONENT_NAME)

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

    emit_log_event(LogLevelEnum.INFO, " | ".join(header_parts), node_id=_COMPONENT_NAME)
    emit_log_event(
        LogLevelEnum.INFO,
        "-" * (sum(col_widths.values()) + len(header_parts) * 3),
        node_id=_COMPONENT_NAME,
    )

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
                    ("Yes" if content_analysis else "No").ljust(col_widths["content"]),
                ]
            )

        emit_log_event(
            LogLevelEnum.INFO, " | ".join(row_parts), node_id=_COMPONENT_NAME
        )

    emit_log_event(
        LogLevelEnum.INFO, f"\nTotal: {len(handlers)} handlers", node_id=_COMPONENT_NAME
    )

    # Print legend
    emit_log_event(LogLevelEnum.INFO, "\nPriority Legend:", node_id=_COMPONENT_NAME)
    emit_log_event(
        LogLevelEnum.INFO,
        "  100+: Core handlers (essential system functionality)",
        node_id=_COMPONENT_NAME,
    )
    emit_log_event(
        LogLevelEnum.INFO,
        "  50-99: Runtime handlers (standard ONEX ecosystem)",
        node_id=_COMPONENT_NAME,
    )
    emit_log_event(
        LogLevelEnum.INFO,
        "  10-49: Node-local handlers (node-specific functionality)",
        node_id=_COMPONENT_NAME,
    )
    emit_log_event(
        LogLevelEnum.INFO,
        "  0-9: Plugin handlers (third-party or experimental)",
        node_id=_COMPONENT_NAME,
    )


if __name__ == "__main__":
    app()
