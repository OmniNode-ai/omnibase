"""
Core logger engine with pluggable output format handlers.

This engine provides the main logging functionality for the logger node,
using a registry of pluggable format handlers to support multiple output
formats (JSON, YAML, Markdown, Text, CSV, etc.).

Enhanced in Phase 2 with context-aware formatting and output targeting.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus, get_event_bus
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.nodes.node_logger.protocols.protocol_logger_engine import ProtocolLoggerEngine

from ..models.logger_output_config import LoggerOutputConfig, create_default_config
from ..models.state import LoggerInputState, LoggerOutputState
from .tool_context_aware_output_handler import (
    ToolContextAwareOutputHandler,
    ToolEnhancedLogFormatter,
)

_COMPONENT_NAME = Path(__file__).stem


class ToolLoggerEngine(ProtocolLoggerEngine):
    """
    Core logger engine with pluggable output format handlers.
    Implements ProtocolLoggerEngine.
    This engine coordinates the formatting of log entries using registered
    format handlers, providing a clean separation between the core logging
    logic and the specific output format implementations.
    Enhanced in Phase 2 with context-aware formatting and output targeting.
    """

    def __init__(
        self,
        handler_registry: Optional[ProtocolNodeRegistry] = None,
        output_config: Optional[LoggerOutputConfig] = None,
        event_bus: Optional[ProtocolEventBus] = None,
    ):
        from ..models.logger_output_config import create_default_config

        self._event_bus = event_bus
        self._output_config = output_config or create_default_config()
        # TODO: Add proper logging once circular dependency is resolved
        
        if handler_registry is None:
            # Create a minimal registry - this will be fixed when circular dependency is resolved
            self._handler_registry = None
        else:
            self._handler_registry = handler_registry
        self.enhanced_formatter = ToolEnhancedLogFormatter(self._output_config)
        self.output_handler = ToolContextAwareOutputHandler(self._output_config)

    def format_log_entry(self, input_state: LoggerInputState) -> str:
        """
        Format a log entry using the appropriate format handler with context-aware enhancements.

        Args:
            input_state: Logger input state containing message, level, format, etc.

        Returns:
            Formatted log entry as a string

        Raises:
            OnexError: If no handler is available for the requested format
                      or if formatting fails
        """
        format_name = input_state.output_format.value
        handler = self._handler_registry.get_handler(format_name)
        if handler is None:
            available_formats = list(self._handler_registry.handled_formats())
            raise OnexError(
                f"No handler available for format '{format_name}'. Available formats: {', '.join(available_formats)}",
                CoreErrorCode.UNSUPPORTED_OPERATION,
            )
        if not handler.validate_dependencies():
            missing_deps = handler.requires_dependencies
            raise OnexError(
                f"Handler for format '{format_name}' has missing dependencies: {missing_deps}",
                CoreErrorCode.DEPENDENCY_UNAVAILABLE,
            )
        base_log_entry = self._build_log_entry(input_state)
        enhanced_log_entry = self.enhanced_formatter.enhance_log_entry(base_log_entry)
        try:
            return handler.format_log_entry(input_state, enhanced_log_entry)
        except Exception as exc:
            raise OnexError(
                f"Failed to format log entry with {format_name} handler: {str(exc)}",
                CoreErrorCode.OPERATION_FAILED,
            ) from exc

    def format_and_output_log_entry(self, input_state: LoggerInputState) -> str:
        """
        Format and output a log entry to configured destinations.

        This is the main method that combines formatting and output routing
        for complete log processing.

        Args:
            input_state: Logger input state containing message, level, format, etc.

        Returns:
            Formatted log entry as a string (same as format_log_entry)

        Raises:
            OnexError: If formatting or output fails
        """
        formatted_log = self.format_log_entry(input_state)
        try:
            self.output_handler.output_log_entry(
                formatted_log, input_state.log_level.value
            )
        except Exception as exc:
            raise OnexError(
                f"Failed to output log entry: {str(exc)}",
                CoreErrorCode.OPERATION_FAILED,
            ) from exc
        return formatted_log

    def _build_log_entry(self, input_state: LoggerInputState) -> Dict[str, Any]:
        """
        Build the base log entry structure.

        Args:
            input_state: Logger input state

        Returns:
            Dictionary containing the structured log entry
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        log_entry: Dict[str, Any] = {
            "timestamp": timestamp,
            "level": input_state.log_level.value.upper(),
            "message": input_state.message,
            "logger": "omnibase.logger_node",
            "version": input_state.version,
        }
        if input_state.context:
            log_entry["context"] = input_state.context
        if input_state.tags:
            log_entry["tags"] = input_state.tags
        if input_state.correlation_id:
            log_entry["correlation_id"] = input_state.correlation_id
        return log_entry

    def list_available_formats(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available output formats and their handlers.

        Returns:
            Dictionary mapping format names to handler metadata
        """
        return self._handler_registry.list_handlers()

    def can_handle_format(self, format_name: str) -> bool:
        """
        Check if a format can be handled.

        Args:
            format_name: Format name to check

        Returns:
            True if a handler is available for this format
        """
        return self._handler_registry.can_handle(format_name)

    def get_format_metadata(self, format_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a specific format.

        Args:
            format_name: Format name to get metadata for

        Returns:
            Format metadata dictionary, or None if format not supported
        """
        handler = self._handler_registry.get_handler(format_name)
        if handler is None:
            return None
        try:
            return handler.get_format_metadata()
        except Exception as exc:
            emit_log_event_sync(
                LogLevelEnum.WARNING,
                f"Failed to get metadata for format {format_name}: {exc}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
            return None

    def register_custom_handler(
        self,
        format_name: str,
        handler: Any,
        source: str = "custom",
        priority: int = 5,
        override: bool = False,
    ) -> None:
        """
        Register a custom format handler.

        Args:
            format_name: Name of the format this handler supports
            handler: Handler instance or class
            source: Source identifier for the handler
            priority: Priority for conflict resolution
            override: Whether to override existing handlers
        """
        self._handler_registry.register_handler(
            format_name=format_name,
            handler=handler,
            source=source,
            priority=priority,
            override=override,
        )

    def update_output_config(self, new_config: LoggerOutputConfig) -> None:
        """
        Update the output configuration and reinitialize handlers.

        Args:
            new_config: New output configuration
        """
        self._output_config = new_config
        self.enhanced_formatter = ToolEnhancedLogFormatter(self._output_config)
        self.output_handler.close()
        self.output_handler = ToolContextAwareOutputHandler(self._output_config)

    def close(self) -> None:
        """
        Close any open resources (file handles, etc.).
        """
        if hasattr(self, "output_handler"):
            self.output_handler.close()

    def __enter__(self) -> "ToolLoggerEngine":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
