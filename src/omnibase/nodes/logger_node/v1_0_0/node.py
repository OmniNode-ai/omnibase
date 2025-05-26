# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node.py
# version: 1.0.0
# uuid: 4f13e6e3-84de-4e5d-8579-f90f3dd41a16
# author: OmniNode Team
# created_at: 2025-05-24T09:29:37.987105
# last_modified_at: 2025-05-25T20:45:00
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5aa9aa96ef80b9158d340ef33ab4819ec2ceeb1f608b2696a9363af138181e5c
# entrypoint: python@node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.node
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Logger Node implementation for structured logging and centralized configuration.

This node provides structured logging capabilities with configurable output formats,
log levels, and integration with the ONEX observability system. It supports
centralized configuration with environment variable overrides.
"""

import logging
import sys
from typing import Callable, Optional

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.error_codes import get_exit_code_for_status
from omnibase.enums import OnexStatus
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)

from .introspection import LoggerNodeIntrospection

# Logger node state models
from .models.state import LoggerInputState, LoggerOutputState

logger = logging.getLogger(__name__)


def run_logger_node(
    input_state: LoggerInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., LoggerOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> LoggerOutputState:
    """
    Main node entrypoint for logger_node.

    Processes log entries with structured formatting, configurable output,
    and integration with the ONEX observability system.

    Args:
        input_state: LoggerInputState (must include version, log_level, message)
        event_bus: ProtocolEventBus (optional, defaults to InMemoryEventBus)
        output_state_cls: Optional callable to construct output state (for testing/mocking)
        handler_registry: Optional FileTypeHandlerRegistry for custom log formatting

    Returns:
        LoggerOutputState (version matches input_state.version)

    Example usage:
        input_state = LoggerInputState(
            version="1.0.0",
            log_level=LogLevel.INFO,
            message="System startup complete",
            context={"node_id": "stamper_node", "operation": "startup"}
        )
        output = run_logger_node(input_state)
    """
    if event_bus is None:
        event_bus = InMemoryEventBus()
    if output_state_cls is None:
        output_state_cls = LoggerOutputState

    # Logger node identifier
    node_id = "logger_node"

    # Emit NODE_START event
    event_bus.publish(
        OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id=node_id,
            metadata={"input_state": input_state.model_dump()},
        )
    )

    try:
        # Import the logger engine
        from .helpers.logger_engine import LoggerEngine

        # Create logger engine instance
        logger_engine = LoggerEngine()

        # Process the log entry with the specified format
        formatted_log = logger_engine.format_log_entry(input_state)

        # Get current timestamp
        from datetime import datetime

        timestamp = datetime.utcnow().isoformat() + "Z"

        # Calculate entry size
        entry_size = len(formatted_log.encode("utf-8"))

        # Create successful output
        result_message = f"Successfully formatted log entry in {input_state.output_format.value} format"

        output = output_state_cls(
            version=input_state.version,
            status="success",
            message=result_message,
            formatted_log=formatted_log,
            output_format=input_state.output_format,
            timestamp=timestamp,
            log_level=input_state.log_level,
            entry_size=entry_size,
        )

        # Emit NODE_SUCCESS event
        event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_SUCCESS,
                node_id=node_id,
                metadata={
                    "input_state": input_state.model_dump(),
                    "output_state": output.model_dump(),
                },
            )
        )

        return output

    except Exception as exc:
        # Emit NODE_FAILURE event
        event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_FAILURE,
                node_id=node_id,
                metadata={
                    "input_state": input_state.model_dump(),
                    "error": str(exc),
                },
            )
        )
        raise


def main() -> None:
    """
    CLI entrypoint for logger node standalone execution.

    Provides command-line interface for the logger node with support for
    all output formats and configuration options.
    """
    import argparse
    import json

    # Create argument parser for logger node
    parser = argparse.ArgumentParser(description="ONEX Logger Node CLI")
    parser.add_argument(
        "--introspect",
        action="store_true",
        help="Display node contract and capabilities",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["debug", "info", "warning", "error", "critical"],
        help="Log level for the message",
    )
    parser.add_argument(
        "--message",
        type=str,
        help="Primary log message content",
    )
    parser.add_argument(
        "--output-format",
        type=str,
        default="json",
        choices=["json", "yaml", "markdown", "text", "csv"],
        help="Output format for the log entry (default: json)",
    )
    parser.add_argument(
        "--context",
        type=str,
        help="JSON string containing additional context data",
    )
    parser.add_argument(
        "--tags",
        type=str,
        help="Comma-separated list of tags for categorizing log entries",
    )
    parser.add_argument(
        "--correlation-id",
        type=str,
        help="Correlation ID for request tracking",
    )

    args = parser.parse_args()

    # Handle introspection command
    if args.introspect:
        LoggerNodeIntrospection.handle_introspect_command()
        return

    # Validate required arguments for normal operation
    if not args.log_level:
        parser.error("--log-level is required when not using --introspect")
    if not args.message:
        parser.error("--message is required when not using --introspect")

    # Parse optional context JSON
    context = None
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError as e:
            parser.error(f"Invalid JSON in --context: {e}")

    # Parse optional tags
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]

    # Get schema version
    schema_version = OnexVersionLoader().get_onex_versions().schema_version

    # Import state models and enums
    from omnibase.enums import LogLevelEnum, OutputFormatEnum

    from .models.state import LoggerInputState

    # Create input state
    input_state = LoggerInputState(
        version=schema_version,
        log_level=LogLevelEnum(args.log_level),
        message=args.message,
        output_format=OutputFormatEnum(args.output_format),
        context=context,
        tags=tags,
        correlation_id=args.correlation_id,
    )

    # Run the node with default event bus for CLI
    output = run_logger_node(input_state)

    # Print the formatted log entry directly
    print(output.formatted_log)

    # Use canonical exit code mapping
    exit_code = get_exit_code_for_status(OnexStatus(output.status))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
