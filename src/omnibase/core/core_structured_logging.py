# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.456035'
# description: Stamped by PythonHandler
# entrypoint: python://core_structured_logging
# hash: fe0b058186c8cd79b1f83b900ea833a533fecb82a242eb352dceab07f834f7d0
# last_modified_at: '2025-05-29T14:13:58.441902+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: core_structured_logging.py
# namespace: python://omnibase.core.core_structured_logging
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 6c905c7e-3bf8-427b-9371-1a9306cb64cf
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Structured Logging Infrastructure for ONEX.

This module implements comprehensive structured logging that routes all internal ONEX 
logging through the Logger Node as side effects, following functional monadic 
architecture principles.

Key Features:
- Complete replacement of print() statements and Python logging
- Event-driven architecture via ProtocolEventBus
- Logger Node handles all output formatting
- Centralized configuration with environment variable support
- Context extraction and correlation ID support
- Fallback mechanisms for robustness

System Flow:
Application Code → emit_log_event() → ProtocolEventBus → StructuredLoggingAdapter → Logger Node → Context-appropriate output
"""

import inspect
import os
import sys
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import LogLevel, OutputFormatEnum
from omnibase.model.model_log_entry import LogContextModel, LogEntryModel
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus


@dataclass
class OnexLoggingConfig:
    """
    Configuration for ONEX structured logging system.

    Supports environment variable configuration following ONEX patterns:
    - ONEX_LOG_FORMAT: Output format (json, yaml, markdown, text, csv)
    - ONEX_LOG_LEVEL: Minimum log level (debug, info, warning, error, critical)
    - ONEX_ENABLE_CORRELATION_IDS: Enable correlation ID generation (true/false)
    - ONEX_LOG_TARGETS: Output targets (stdout, file, etc.)
    - ONEX_LOG_FILE_PATH: File path for file output
    - ONEX_EVENT_BUS_TYPE: Event bus implementation type
    """

    # Logger Node configuration
    default_output_format: OutputFormatEnum = OutputFormatEnum.JSON
    log_level: LogLevel = LogLevel.INFO

    # Event bus configuration
    enable_correlation_ids: bool = True
    event_bus_type: str = "InMemoryEventBus"

    # Output configuration
    log_targets: list[str] = field(default_factory=lambda: ["stdout"])
    log_file_path: Optional[str] = None

    # Context configuration
    include_caller_info: bool = True
    include_timestamps: bool = True

    @classmethod
    def from_environment(cls) -> "OnexLoggingConfig":
        """
        Create configuration from environment variables.

        Returns:
            OnexLoggingConfig instance with values from environment
        """
        # Parse output format
        format_str = os.environ.get("ONEX_LOG_FORMAT", "json").lower()
        try:
            output_format = OutputFormatEnum(format_str)
        except ValueError:
            output_format = OutputFormatEnum.JSON

        # Parse log level
        level_str = os.environ.get("ONEX_LOG_LEVEL", "info").lower()
        try:
            log_level = LogLevel(level_str)
        except ValueError:
            log_level = LogLevel.INFO

        # Parse boolean flags
        enable_correlation_ids = (
            os.environ.get("ONEX_ENABLE_CORRELATION_IDS", "true").lower() == "true"
        )
        include_caller_info = (
            os.environ.get("ONEX_INCLUDE_CALLER_INFO", "true").lower() == "true"
        )
        include_timestamps = (
            os.environ.get("ONEX_INCLUDE_TIMESTAMPS", "true").lower() == "true"
        )

        # Parse targets
        targets_str = os.environ.get("ONEX_LOG_TARGETS", "stdout")
        log_targets = [target.strip() for target in targets_str.split(",")]

        # File path
        log_file_path = os.environ.get("ONEX_LOG_FILE_PATH")

        # Event bus type
        event_bus_type = os.environ.get("ONEX_EVENT_BUS_TYPE", "InMemoryEventBus")

        return cls(
            default_output_format=output_format,
            log_level=log_level,
            enable_correlation_ids=enable_correlation_ids,
            event_bus_type=event_bus_type,
            log_targets=log_targets,
            log_file_path=log_file_path,
            include_caller_info=include_caller_info,
            include_timestamps=include_timestamps,
        )


class StructuredLoggingAdapter:
    """
    Adapter that subscribes to log events and routes them through the Logger Node.

    This class implements the core routing logic that takes STRUCTURED_LOG events
    from the event bus and processes them through the Logger Node for formatting
    and output. Only strongly typed LogContextModel and LogLevel are accepted.
    """

    def __init__(self, config: OnexLoggingConfig, event_bus: "ProtocolEventBus"):
        self.config = config
        self.event_bus = event_bus

    def _handle_log_event(self, event: OnexEvent) -> None:
        if event.event_type != OnexEventTypeEnum.STRUCTURED_LOG:
            return

        metadata = event.metadata
        if not metadata or not isinstance(metadata, dict):
            return
        context = metadata.get("context", None)
        if not isinstance(context, LogContextModel):
            raise TypeError(
                "StructuredLoggingAdapter expects context to be LogContextModel"
            )
        source_module = context.calling_module
        if source_module.startswith("omnibase.nodes.logger_node"):
            return
        try:
            message = metadata.get("message", "")
            log_level = metadata.get("log_level", LogLevel.INFO)
            if not isinstance(log_level, LogLevel):
                raise TypeError(
                    "StructuredLoggingAdapter expects log_level to be LogLevel"
                )
            log_entry = LogEntryModel(
                message=message,
                level=log_level,
                context=context,
            )
            self.event_bus.publish(log_entry)
        except Exception as exc:
            fallback_message = f"[STRUCTURED_LOG_FALLBACK] {metadata.get('message', 'Unknown log message')}"
            print(fallback_message, file=sys.stderr)
            print(f"[STRUCTURED_LOG_ERROR] {exc}", file=sys.stderr)

    def _output_log(self, formatted_log: str) -> None:
        """
        Output the formatted log to configured targets.

        Args:
            formatted_log: The formatted log string to output
        """
        for target in self.config.log_targets:
            if target == "stdout":
                print(formatted_log, file=sys.stdout)
            elif target == "stderr":
                print(formatted_log, file=sys.stderr)
            elif target == "file" and self.config.log_file_path:
                try:
                    with open(self.config.log_file_path, "a", encoding="utf-8") as f:
                        f.write(formatted_log + "\n")
                except Exception as e:
                    print(
                        f"[LOG_FILE_ERROR] Failed to write to {self.config.log_file_path}: {e}",
                        file=sys.stderr,
                    )


# Global state for structured logging
_global_config: Optional[OnexLoggingConfig] = None
_global_event_bus: Optional["ProtocolEventBus"] = None
_global_adapter: Optional[StructuredLoggingAdapter] = None
_auto_initialized: bool = False


def _get_calling_module() -> str:
    """
    Extract the calling module name from the call stack.

    Returns:
        Module name of the caller
    """
    frame = inspect.currentframe()
    try:
        # Go up the stack to find the actual caller (skip this function and emit_log_event)
        caller_frame = (
            frame.f_back.f_back.f_back
            if frame and frame.f_back and frame.f_back.f_back
            else None
        )
        if caller_frame:
            module_name = caller_frame.f_globals.get("__name__", "unknown")
            return str(module_name)
        return "unknown"
    finally:
        del frame


def _get_calling_function() -> str:
    """
    Extract the calling function name from the call stack.

    Returns:
        Function name of the caller
    """
    frame = inspect.currentframe()
    try:
        # Go up the stack to find the actual caller
        caller_frame = (
            frame.f_back.f_back.f_back
            if frame and frame.f_back and frame.f_back.f_back
            else None
        )
        if caller_frame:
            return caller_frame.f_code.co_name
        return "unknown"
    finally:
        del frame


def _get_calling_line() -> int:
    """
    Extract the calling line number from the call stack.

    Returns:
        Line number of the caller
    """
    frame = inspect.currentframe()
    try:
        # Go up the stack to find the actual caller
        caller_frame = (
            frame.f_back.f_back.f_back
            if frame and frame.f_back and frame.f_back.f_back
            else None
        )
        if caller_frame:
            return caller_frame.f_lineno
        return 0
    finally:
        del frame


def emit_log_event(
    level: LogLevel,
    message: str,
    context: Optional[LogContextModel] = None,
    correlation_id: Optional[str] = None,
    node_id: Optional[str] = None,
    event_bus: "ProtocolEventBus" = None,
    event_type: Optional[OnexEventTypeEnum] = None,
) -> None:
    """
    Primary function for emitting structured log events.

    This function replaces all print() statements and Python logging calls
    throughout the ONEX codebase. It emits structured events that are routed
    through the Logger Node for consistent formatting and output.

    Recursion Guard:
        Prevents infinite recursion if log emission itself triggers another log event.
        Uses a thread-local flag to detect re-entrant calls.
    """
    # Recursion guard (thread-local)
    if not hasattr(emit_log_event, "_thread_local"):
        emit_log_event._thread_local = threading.local()
    if getattr(emit_log_event._thread_local, "in_emit_log_event", False):
        # Optionally, print to stderr as a fallback or just silently drop
        return
    emit_log_event._thread_local.in_emit_log_event = True
    try:
        if event_bus is None:
            raise RuntimeError(
                "emit_log_event requires an explicit event_bus argument (protocol purity)"
            )

        if not isinstance(level, LogLevel):
            raise TypeError("level must be a LogLevel, not a string or other type")

        if context is not None and not isinstance(context, LogContextModel):
            raise TypeError(
                "context must be a LogContextModel, not a dict or other type"
            )

        # Generate correlation ID if not provided
        if correlation_id is None:
            correlation_id = str(uuid4())

        # Determine node ID
        if node_id is None:
            node_id = _get_calling_module()

        # Build strongly typed context
        if context is None:
            typed_context = LogContextModel(
                calling_module=_get_calling_module(),
                calling_function=_get_calling_function(),
                calling_line=_get_calling_line(),
                timestamp=datetime.utcnow().isoformat() + "Z",
                node_id=node_id,
                correlation_id=correlation_id,
            )
        else:
            typed_context = context

        # Print directly for logger_node or CLI handler listing
        if node_id in {"logger_node", "list_handlers", "list_handlers.py"}:
            print(message)
            return

        # Use provided event_type or default to STRUCTURED_LOG
        event_type = event_type or OnexEventTypeEnum.STRUCTURED_LOG

        # Use LogEntryModel as metadata for protocol-pure logging
        log_entry = LogEntryModel(message=message, level=level, context=typed_context)
        event = OnexEvent(
            node_id=node_id,
            event_type=event_type,
            correlation_id=correlation_id,
            metadata=log_entry,
        )
        event_bus.publish(event)
    finally:
        emit_log_event._thread_local.in_emit_log_event = False


def structured_print(
    *args: Any,
    event_bus: "ProtocolEventBus" = None,
    context: Optional[LogContextModel] = None,
    **kwargs: Any,
) -> None:
    """
    Migration helper function that replaces print() calls.

    This function provides a drop-in replacement for print() statements
    during the migration phase. It converts print() calls to structured
    log events at INFO level.

    Args:
        *args: Arguments to print (will be joined as message)
        event_bus: Event bus for protocol-pure logging (required)
        context: Optional LogContextModel for context
        **kwargs: Keyword arguments (file, sep, end are ignored)
    """
    # Convert args to message string
    message = " ".join(str(arg) for arg in args)

    if context is not None and not isinstance(context, LogContextModel):
        raise TypeError("context must be a LogContextModel, not a dict or other type")

    # Emit as INFO level log event
    emit_log_event(LogLevel.INFO, message, context=context, event_bus=event_bus)


def setup_structured_logging(
    config: Optional[OnexLoggingConfig] = None,
    event_bus: Optional["ProtocolEventBus"] = None,
) -> None:
    """
    Global setup function for structured logging system.

    This function initializes the structured logging infrastructure and
    disables Python logging to ensure all output flows through the Logger Node.

    Args:
        config: Optional logging configuration (defaults to environment-based)
        event_bus: Optional event bus (defaults to InMemoryEventBus)
    """
    global _global_config, _global_event_bus, _global_adapter, _auto_initialized

    # Use provided config or create from environment
    if config is None:
        config = OnexLoggingConfig.from_environment()
    _global_config = config

    # Use provided event bus or create default
    if event_bus is None:
        # Protocol purity: use a local fallback event bus for test/dev only
        class FallbackEventBus(ProtocolEventBus):
            def __init__(self) -> None:
                self._subscribers: set[Any] = set()

            def publish(self, event: Any) -> None:
                for sub in list(self._subscribers):
                    try:
                        sub(event)
                    except Exception:
                        pass

            def subscribe(self, callback: Any) -> None:
                self._subscribers.add(callback)

            def unsubscribe(self, callback: Any) -> None:
                self._subscribers.discard(callback)

        event_bus = FallbackEventBus()
    _global_event_bus = event_bus

    # Create and initialize the adapter
    _global_adapter = StructuredLoggingAdapter(config, event_bus)

    # Now that the adapter is initialized, subscribe it to the event bus
    # This prevents circular dependency during initialization
    event_bus.subscribe(_global_adapter._handle_log_event)

    # Mark as initialized
    _auto_initialized = True


# Testing utilities
def reset_structured_logging() -> None:
    """
    Reset structured logging state for testing.

    This function clears all global state and re-enables Python logging.
    Used primarily in test teardown.
    """
    global _global_config, _global_event_bus, _global_adapter, _auto_initialized

    _global_config = None
    _global_event_bus = None
    _global_adapter = None
    _auto_initialized = False


def get_global_config() -> Optional[OnexLoggingConfig]:
    """Get the current global logging configuration."""
    return _global_config


def get_global_event_bus() -> Optional["ProtocolEventBus"]:
    """Get the current global event bus."""
    return _global_event_bus


def get_global_adapter() -> Optional[StructuredLoggingAdapter]:
    """Get the current global logging adapter."""
    return _global_adapter


def is_auto_initialized() -> bool:
    """Check if structured logging has been auto-initialized."""
    return _auto_initialized
