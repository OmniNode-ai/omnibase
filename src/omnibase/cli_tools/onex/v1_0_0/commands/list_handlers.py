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
from pydantic import BaseModel, Field

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevel
from omnibase.enums.handler_source import HandlerSourceEnum
from omnibase.model.model_handler_protocol import HandlerMetadataModel
from omnibase.model.model_log_entry import LogContextModel
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)

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


class HandlerInfoCLIModel(HandlerMetadataModel):
    type: str = Field(..., description="Handler type: extension, special, or named")
    key: str = Field(..., description="Handler key: extension, filename, or name")
    handler_class: str = Field(..., description="Handler class name")
    priority: int = Field(..., description="Registration priority")
    override: bool = Field(..., description="Override flag")


@app.command("list")
def list_handlers(
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, or summary"
    ),
    source_filter: Optional[HandlerSourceEnum] = typer.Option(
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
    # Create event bus for protocol-pure logging
    event_bus = InMemoryEventBus()

    # Get the registry and populate it with all available handlers
    registry = FileTypeHandlerRegistry(event_bus=event_bus)
    registry.register_all_handlers()

    # Get all handlers
    all_handlers = registry.list_handlers()

    # Convert all handler dicts to HandlerInfoCLIModel
    handler_models = {
        handler_id: HandlerInfoCLIModel(**handler_info)
        for handler_id, handler_info in all_handlers.items()
    }

    # Apply filters
    filtered_handlers = {}
    for handler_id, handler_model in handler_models.items():
        # Apply source filter
        if source_filter and handler_model.source != source_filter:
            continue
        # Apply type filter
        if type_filter and handler_model.type != type_filter:
            continue
        filtered_handlers[handler_id] = handler_model

    if not filtered_handlers:
        emit_log_event(
            LogLevel.INFO,
            "No handlers found matching the specified filters.",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="list_handlers",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )
        return

    # Output based on format
    if format_type == "json":
        # For JSON format, print model_dump of HandlerInfoCLIModel
        print(
            json.dumps(
                {k: v.model_dump() for k, v in filtered_handlers.items()},
                indent=2,
                default=str,
            )
        )
    elif format_type == "summary":
        _print_summary(filtered_handlers, event_bus)
    else:  # table format (default)
        _print_table(filtered_handlers, show_metadata, verbose, event_bus)


def _print_summary(handlers: Dict[str, HandlerInfoCLIModel], event_bus) -> None:
    """Print a summary of handlers by source and type."""
    # Debug: print all handler keys being processed
    emit_log_event(
        LogLevel.DEBUG,
        f"[DEBUG] _print_summary: handler keys: {list(handlers.keys())}",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_summary",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )
    # Count by source
    source_counts: Dict[str, int] = {}
    type_counts: Dict[str, int] = {}

    for handler_model in handlers.values():
        source = handler_model.source.value
        source_counts[source] = source_counts.get(source, 0) + 1
        handler_type = handler_model.type
        type_counts[handler_type] = type_counts.get(handler_type, 0) + 1

    emit_log_event(
        LogLevel.INFO,
        "\nHandler Summary",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_summary",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )
    emit_log_event(
        LogLevel.INFO,
        "=" * 50,
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_summary",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

    emit_log_event(
        LogLevel.INFO,
        f"\nTotal Handlers: {len(handlers)}",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_summary",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

    emit_log_event(
        LogLevel.INFO,
        "\nBy Source:",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_summary",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )
    for source, count in sorted(source_counts.items()):
        emit_log_event(
            LogLevel.INFO,
            f"  {source}: {count}",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="_print_summary",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )

    emit_log_event(
        LogLevel.INFO,
        "\nBy Type:",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_summary",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )
    for handler_type, count in sorted(type_counts.items()):
        emit_log_event(
            LogLevel.INFO,
            f"  {handler_type}: {count}",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="_print_summary",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )


def _print_table(
    handlers: dict[str, HandlerInfoCLIModel],
    show_metadata: bool,
    verbose: bool,
    event_bus,
) -> None:
    """Print handlers in a formatted table."""
    # Debug: print all handler keys being processed
    emit_log_event(
        LogLevel.DEBUG,
        f"[DEBUG] _print_table: handler keys: {list(handlers.keys())}",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_table",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )
    if verbose:
        show_metadata = True

    emit_log_event(
        LogLevel.INFO,
        "\nRegistered File Type Handlers",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_table",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )
    emit_log_event(
        LogLevel.INFO,
        "=" * 80,
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_table",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

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

    emit_log_event(
        LogLevel.INFO,
        " | ".join(header_parts),
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_table",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )
    emit_log_event(
        LogLevel.INFO,
        "-" * (sum(col_widths.values()) + len(header_parts) * 3),
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_table",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

    # Print rows
    for handler_id, handler_model in sorted(handlers.items()):
        row_parts = [
            handler_id[: col_widths["id"]].ljust(col_widths["id"]),
            handler_model.type[: col_widths["type"]].ljust(col_widths["type"]),
            handler_model.key[: col_widths["key"]].ljust(col_widths["key"]),
            handler_model.handler_class[: col_widths["class"]].ljust(
                col_widths["class"]
            ),
            handler_model.source.value[: col_widths["source"]].ljust(
                col_widths["source"]
            ),
            str(handler_model.priority)[: col_widths["priority"]].ljust(
                col_widths["priority"]
            ),
        ]
        if show_metadata:
            row_parts.extend(
                [
                    handler_model.handler_name[: col_widths["name"]].ljust(
                        col_widths["name"]
                    ),
                    handler_model.handler_version[: col_widths["version"]].ljust(
                        col_widths["version"]
                    ),
                    handler_model.handler_author[: col_widths["author"]].ljust(
                        col_widths["author"]
                    ),
                    handler_model.handler_description[
                        : col_widths["description"]
                    ].ljust(col_widths["description"]),
                ]
            )
        if verbose:
            row_parts.extend(
                [
                    format_extensions_list(handler_model.supported_extensions)[
                        : col_widths["extensions"]
                    ].ljust(col_widths["extensions"]),
                    format_filenames_list(handler_model.supported_filenames)[
                        : col_widths["files"]
                    ].ljust(col_widths["files"]),
                    ("Yes" if handler_model.requires_content_analysis else "No").ljust(
                        col_widths["content"]
                    ),
                ]
            )
        emit_log_event(
            LogLevel.INFO,
            " | ".join(row_parts),
            context=LogContextModel(
                calling_module=__name__,
                calling_function="_print_table",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )

    emit_log_event(
        LogLevel.INFO,
        f"\nTotal: {len(handlers)} handlers",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_table",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

    # Print legend
    emit_log_event(
        LogLevel.INFO,
        "\nPriority Legend:",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_table",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )
    emit_log_event(
        LogLevel.INFO,
        "  100+: Core handlers (essential system functionality)",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_table",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )
    emit_log_event(
        LogLevel.INFO,
        "  50-99: Runtime handlers (standard ONEX ecosystem)",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_table",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )
    emit_log_event(
        LogLevel.INFO,
        "  10-49: Node-local handlers (node-specific functionality)",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_table",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )
    emit_log_event(
        LogLevel.INFO,
        "  0-9: Plugin handlers (third-party or experimental)",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="_print_table",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )


if __name__ == "__main__":
    app()
