# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: core_structured_logging.py
# version: 1.0.0
# uuid: b6d526b8-0895-4773-b36a-46e487de50e9
# author: OmniNode Team
# created_at: 2025-05-26T15:47:37.841917
# last_modified_at: 2025-05-27T16:29:37.384397
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b0903901a052c9a77ea9340a900c3685ce1593ac9d2785f90a25f55461262bad
# entrypoint: python@core_structured_logging.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.core_structured_logging
# meta_type: tool
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
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import LogLevelEnum, OutputFormatEnum
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus


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
    log_level: LogLevelEnum = LogLevelEnum.INFO

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
            log_level = LogLevelEnum(level_str)
        except ValueError:
            log_level = LogLevelEnum.INFO

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
    and output.
    """

    def __init__(self, config: OnexLoggingConfig, event_bus: ProtocolEventBus):
        """
        Initialize the structured logging adapter.

        Args:
            config: Logging configuration
            event_bus: Event bus for subscribing to log events
        """
        self.config = config
        self.event_bus = event_bus
        self._logger_node_runner: Optional[Any] = None

        # IMPORTANT: We're NOT subscribing here to avoid circular dependency
        # The subscription will be done by setup_structured_logging after initialization

    def _get_logger_node_runner(self) -> Any:
        """
        Lazy-load the Logger Node runner to avoid circular imports.

        Returns:
            Logger Node runner function
        """
        if self._logger_node_runner is None:
            try:
                from omnibase.nodes.logger_node.v1_0_0.node import run_logger_node

                self._logger_node_runner = run_logger_node
            except ImportError as e:
                raise OnexError(
                    f"Failed to import Logger Node: {e}",
                    CoreErrorCode.DEPENDENCY_UNAVAILABLE,
                )
        return self._logger_node_runner

    def _handle_log_event(self, event: OnexEvent) -> None:
        """
        Handle a structured log event by routing it through the Logger Node.

        Args:
            event: The structured log event to process
        """
        # Filter for only structured log events
        if event.event_type != OnexEventTypeEnum.STRUCTURED_LOG:
            return

        # Safety check - Logger Node may emit logs during processing which
        # could lead to recursion. Check if we're already processing this event.
        # Use source information to detect potential recursion
        metadata = event.metadata or {}
        context = metadata.get("context", {})
        source_module = context.get("calling_module", "")
        if source_module.startswith("omnibase.nodes.logger_node"):
            # Skip logs from the logger node itself to prevent recursion
            return

        try:
            # Extract log information from event metadata
            metadata = event.metadata or {}
            message = metadata.get("message", "")
            context = metadata.get("context", {})
            correlation_id = metadata.get("correlation_id") or event.correlation_id

            # Import Logger Node state models
            from omnibase.nodes.logger_node.v1_0_0.models.state import LoggerInputState

            # Create LoggerInputState from event
            input_state = LoggerInputState(
                version="1.0.0",
                log_level=LogLevelEnum(
                    metadata.get("log_level", LogLevelEnum.INFO.value)
                ),
                message=message,
                output_format=self.config.default_output_format,
                context=context,
                correlation_id=correlation_id,
            )

            # Route through Logger Node
            logger_node_runner = self._get_logger_node_runner()
            output_state = logger_node_runner(input_state, self.event_bus)

            # Output the formatted log based on targets
            formatted_log = output_state.formatted_log
            self._output_log(formatted_log)

        except Exception as exc:
            # Fallback to direct print if Logger Node fails
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
_global_event_bus: Optional[ProtocolEventBus] = None
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
    level: Union[LogLevelEnum, str],
    message: str,
    context: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    node_id: Optional[str] = None,
) -> None:
    """
    Primary function for emitting structured log events.

    This function replaces all print() statements and Python logging calls
    throughout the ONEX codebase. It emits structured events that are routed
    through the Logger Node for consistent formatting and output.

    Args:
        level: Log level (LogLevelEnum or string)
        message: Primary log message content
        context: Additional context data to include
        correlation_id: Optional correlation ID for tracing
        node_id: Optional node ID (defaults to calling module)

    Example:
        emit_log_event(LogLevelEnum.INFO, "Processing file", {"filename": "data.json"})
        emit_log_event("error", "Operation failed", {"error_code": "ONEX_001"})
    """
    global _global_config, _global_event_bus, _global_adapter, _auto_initialized

    # Auto-initialize if not already done
    if not _auto_initialized:
        # We need to handle potential recursion during initialization
        # Flag that we're starting to initialize to prevent infinite recursion
        _auto_initialized = True
        try:
            setup_structured_logging()
        except Exception as e:
            # If initialization fails, reset flag and use fallback
            _auto_initialized = False
            print(
                f"[SETUP_ERROR] Failed to initialize structured logging: {e}",
                file=sys.stderr,
            )
            print(f"[FALLBACK] {level}: {message}", file=sys.stderr)
            return

    # Ensure we have required components
    if _global_event_bus is None:
        # Fallback to direct print if event bus is not available
        print(f"[FALLBACK] {level}: {message}", file=sys.stderr)
        return

    # Convert string level to enum
    if isinstance(level, str):
        try:
            level = LogLevelEnum(level.lower())
        except ValueError:
            level = LogLevelEnum.INFO

    # Generate correlation ID if enabled and not provided
    if (
        correlation_id is None
        and _global_config
        and _global_config.enable_correlation_ids
    ):
        correlation_id = str(uuid4())

    # Extract caller information if enabled
    caller_context = {}
    if _global_config and _global_config.include_caller_info:
        caller_context.update(
            {
                "calling_module": _get_calling_module(),
                "calling_function": _get_calling_function(),
                "calling_line": _get_calling_line(),
            }
        )

    # Merge context with caller information
    full_context = {**(context or {}), **caller_context}

    # Add timestamp if enabled
    if _global_config and _global_config.include_timestamps:
        full_context["timestamp"] = datetime.utcnow().isoformat() + "Z"

    # Determine node ID
    if node_id is None:
        node_id = _get_calling_module()

    # Create and emit the structured log event
    log_event = OnexEvent(
        event_type=OnexEventTypeEnum.STRUCTURED_LOG,
        node_id=node_id,
        correlation_id=correlation_id,
        metadata={
            "log_level": level.value,
            "message": message,
            "context": full_context,
            "correlation_id": correlation_id,
        },
    )

    try:
        _global_event_bus.publish(log_event)
    except Exception as exc:
        # Fallback to direct print if event publishing fails
        print(f"[FALLBACK] {level.value}: {message}", file=sys.stderr)
        print(f"[EVENT_BUS_ERROR] {exc}", file=sys.stderr)


def structured_print(*args: Any, **kwargs: Any) -> None:
    """
    Migration helper function that replaces print() calls.

    This function provides a drop-in replacement for print() statements
    during the migration phase. It converts print() calls to structured
    log events at INFO level.

    Args:
        *args: Arguments to print (will be joined as message)
        **kwargs: Keyword arguments (file, sep, end are ignored)
    """
    # Convert args to message string
    message = " ".join(str(arg) for arg in args)

    # Extract context from kwargs if present
    context = {}
    if "file" in kwargs:
        context["original_file"] = str(kwargs["file"])

    # Emit as INFO level log event
    emit_log_event(LogLevelEnum.INFO, message, context=context)


def setup_structured_logging(
    config: Optional[OnexLoggingConfig] = None,
    event_bus: Optional[ProtocolEventBus] = None,
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
        # CRITICAL: We use a direct import and instantiation with no logging
        # to avoid circular dependencies during initialization
        try:
            from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
                InMemoryEventBus,
            )

            # Create a clean instance with no subscribers
            event_bus = InMemoryEventBus()
        except Exception as e:
            print(f"[CRITICAL] Failed to create event bus: {e}", file=sys.stderr)
            # Create a minimal fallback event bus
            from omnibase.core.events import ProtocolEventBus  # type: ignore

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


def get_global_event_bus() -> Optional[ProtocolEventBus]:
    """Get the current global event bus."""
    return _global_event_bus


def get_global_adapter() -> Optional[StructuredLoggingAdapter]:
    """Get the current global logging adapter."""
    return _global_adapter


def is_auto_initialized() -> bool:
    """Check if structured logging has been auto-initialized."""
    return _auto_initialized
