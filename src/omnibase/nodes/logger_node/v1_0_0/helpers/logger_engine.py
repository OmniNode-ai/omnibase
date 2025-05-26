# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: logger_engine.py
# version: 1.0.0
# uuid: 90dc884b-2713-4f79-9e3b-abbe6564cfd9
# author: OmniNode Team
# created_at: 2025-05-26T12:30:48.005986
# last_modified_at: 2025-05-26T16:53:38.719982
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: df286775a70d108ea4a1b76da6e7b7d5dd70a8232eff600323e7a557dd113e50
# entrypoint: python@logger_engine.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.logger_engine
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Core logger engine with pluggable output format handlers.

This engine provides the main logging functionality for the logger node,
using a registry of pluggable format handlers to support multiple output
formats (JSON, YAML, Markdown, Text, CSV, etc.).
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from omnibase.core.error_codes import CoreErrorCode, OnexError

from ..models.state import LoggerInputState
from ..registry.log_format_handler_registry import LogFormatHandlerRegistry


class LoggerEngine:
    """
    Core logger engine with pluggable output format handlers.

    This engine coordinates the formatting of log entries using registered
    format handlers, providing a clean separation between the core logging
    logic and the specific output format implementations.
    """

    def __init__(self, handler_registry: Optional[LogFormatHandlerRegistry] = None):
        """
        Initialize the logger engine.

        Args:
            handler_registry: Optional registry for format handlers.
                             If None, creates a new registry with all handlers.
        """
        self._logger = logging.getLogger("omnibase.LoggerEngine")

        if handler_registry is None:
            self._handler_registry = LogFormatHandlerRegistry()
            self._handler_registry.register_all_handlers()
        else:
            self._handler_registry = handler_registry

    def format_log_entry(self, input_state: LoggerInputState) -> str:
        """
        Format a log entry using the appropriate format handler.

        Args:
            input_state: Logger input state containing message, level, format, etc.

        Returns:
            Formatted log entry as a string

        Raises:
            OnexError: If no handler is available for the requested format
                      or if formatting fails
        """
        # Get the format handler
        format_name = input_state.output_format.value
        handler = self._handler_registry.get_handler(format_name)

        if handler is None:
            available_formats = list(self._handler_registry.handled_formats())
            raise OnexError(
                f"No handler available for format '{format_name}'. "
                f"Available formats: {', '.join(available_formats)}",
                CoreErrorCode.UNSUPPORTED_OPERATION,
            )

        # Validate handler dependencies
        if not handler.validate_dependencies():
            missing_deps = handler.requires_dependencies
            raise OnexError(
                f"Handler for format '{format_name}' has missing dependencies: {missing_deps}",
                CoreErrorCode.DEPENDENCY_UNAVAILABLE,
            )

        # Build the base log entry structure
        log_entry = self._build_log_entry(input_state)

        # Format using the handler
        try:
            return handler.format_log_entry(input_state, log_entry)
        except Exception as exc:
            raise OnexError(
                f"Failed to format log entry with {format_name} handler: {str(exc)}",
                CoreErrorCode.OPERATION_FAILED,
            ) from exc

    def _build_log_entry(self, input_state: LoggerInputState) -> Dict[str, Any]:
        """
        Build the base log entry structure.

        Args:
            input_state: Logger input state

        Returns:
            Dictionary containing the structured log entry
        """
        # Generate timestamp
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Build base log entry
        log_entry: Dict[str, Any] = {
            "timestamp": timestamp,
            "level": input_state.log_level.value.upper(),
            "message": input_state.message,
            "logger": "omnibase.logger_node",
            "version": input_state.version,
        }

        # Add optional fields if present
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
            self._logger.warning(
                f"Failed to get metadata for format {format_name}: {exc}"
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
