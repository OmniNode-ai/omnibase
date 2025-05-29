# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.036518'
# description: Stamped by PythonHandler
# entrypoint: python://context_aware_output_handler.py
# hash: 0c92538f8821b87fd0f3f9ff3dcd4847c722b138b75d29c829fac0a94c3bceba
# last_modified_at: '2025-05-29T11:50:11.280556+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: context_aware_output_handler.py
# namespace: omnibase.context_aware_output_handler
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 26efd30d-7b0d-41d4-9417-ea7da59148bc
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Context-aware output handler for Logger Node.

Handles the actual output of formatted log entries to various destinations
(stdout, stderr, file) based on LoggerOutputConfig settings and environment
context.

This supports Phase 2 of the structured logging infrastructure implementation.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional, TextIO

from omnibase.core.core_error_codes import CoreErrorCode, OnexError

from ..models.logger_output_config import LoggerOutputConfig


class ContextAwareOutputHandler:
    """
    Context-aware output handler for Logger Node.

    Routes formatted log entries to appropriate destinations based on
    configuration and environment context, with support for multiple
    output targets and format-specific handling.
    """

    def __init__(self, config: LoggerOutputConfig):
        """
        Initialize the output handler.

        Args:
            config: Logger output configuration
        """
        self.config = config
        self._file_handle: Optional[TextIO] = None
        self._file_path: Optional[str] = None

    def output_log_entry(self, formatted_log: str, log_level: str) -> None:
        """
        Output a formatted log entry to configured destinations.

        Args:
            formatted_log: The formatted log entry string
            log_level: Log level for routing decisions (error -> stderr)

        Raises:
            OnexError: If output operation fails
        """
        try:
            # Determine if this should go to stderr based on log level
            is_error_level = log_level.lower() in ("error", "critical")

            # Handle stdout output
            if self.config.should_output_to_stdout() and not is_error_level:
                self._write_to_stream(sys.stdout, formatted_log)

            # Handle stderr output (or error-level messages)
            if self.config.should_output_to_stderr() or is_error_level:
                self._write_to_stream(sys.stderr, formatted_log)

            # Handle file output
            if self.config.should_output_to_file():
                self._write_to_file(formatted_log)

        except Exception as exc:
            raise OnexError(
                f"Failed to output log entry: {str(exc)}",
                CoreErrorCode.OPERATION_FAILED,
            ) from exc

    def _write_to_stream(self, stream: TextIO, content: str) -> None:
        """
        Write content to a stream (stdout/stderr).

        Args:
            stream: Output stream
            content: Content to write
        """
        try:
            # Add newline if not present
            if not content.endswith("\n"):
                content += "\n"

            stream.write(content)
            stream.flush()

        except Exception as exc:
            raise OnexError(
                f"Failed to write to stream: {str(exc)}", CoreErrorCode.OPERATION_FAILED
            ) from exc

    def _write_to_file(self, content: str) -> None:
        """
        Write content to configured file.

        Args:
            content: Content to write
        """
        if not self.config.file_path:
            raise OnexError(
                "File output requested but no file_path configured",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )

        try:
            # Ensure file handle is open
            self._ensure_file_handle()

            if self._file_handle:
                # Add newline if not present
                if not content.endswith("\n"):
                    content += "\n"

                self._file_handle.write(content)
                self._file_handle.flush()

        except Exception as exc:
            raise OnexError(
                f"Failed to write to file {self.config.file_path}: {str(exc)}",
                CoreErrorCode.OPERATION_FAILED,
            ) from exc

    def _ensure_file_handle(self) -> None:
        """
        Ensure file handle is open and ready for writing.
        """
        if not self.config.file_path:
            return

        # Check if we need to open/reopen the file
        if (
            self._file_handle is None
            or self._file_path != self.config.file_path
            or self._file_handle.closed
        ):

            # Close existing handle if open
            if self._file_handle and not self._file_handle.closed:
                self._file_handle.close()

            try:
                # Create directory if it doesn't exist
                file_path = Path(self.config.file_path)
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Open file for appending
                self._file_handle = open(file_path, "a", encoding="utf-8")
                self._file_path = self.config.file_path

            except Exception as exc:
                raise OnexError(
                    f"Failed to open log file {self.config.file_path}: {str(exc)}",
                    CoreErrorCode.OPERATION_FAILED,
                ) from exc

    def close(self) -> None:
        """
        Close any open file handles.
        """
        if self._file_handle and not self._file_handle.closed:
            try:
                self._file_handle.close()
            except Exception:
                # Ignore errors during cleanup
                pass
            finally:
                self._file_handle = None
                self._file_path = None

    def __enter__(self) -> "ContextAwareOutputHandler":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


class EnhancedLogFormatter:
    """
    Enhanced log formatter that applies context-aware formatting.

    Uses LoggerOutputConfig settings to control what fields are included
    and how they are formatted based on environment and verbosity.
    """

    def __init__(self, config: LoggerOutputConfig):
        """
        Initialize the formatter.

        Args:
            config: Logger output configuration
        """
        self.config = config
        self.format_settings = config.get_effective_format_settings()

    def enhance_log_entry(self, base_log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance a base log entry with context-aware formatting.

        Args:
            base_log_entry: Base log entry dictionary

        Returns:
            Enhanced log entry with applied formatting settings
        """
        enhanced_entry: Dict[str, Any] = {}

        # Always include message and level
        enhanced_entry["message"] = self._format_message(
            base_log_entry.get("message", "")
        )
        enhanced_entry["level"] = base_log_entry.get("level", "INFO")

        # Conditionally include other fields based on settings
        if self.format_settings.get("include_timestamp", True):
            timestamp = base_log_entry.get("timestamp")
            if timestamp is not None:
                enhanced_entry["timestamp"] = str(timestamp)

        if self.format_settings.get("include_correlation_id", True):
            correlation_id = base_log_entry.get("correlation_id")
            if correlation_id:
                enhanced_entry["correlation_id"] = correlation_id

        if self.format_settings.get("include_context", True):
            context = base_log_entry.get("context")
            if context and isinstance(context, dict):
                enhanced_entry["context"] = self._format_context(context)

        if self.format_settings.get("include_tags", True):
            tags = base_log_entry.get("tags")
            if tags:
                enhanced_entry["tags"] = tags

        # Add logger and version info for verbose/debug modes
        if self.config.verbosity.value in ("verbose", "debug"):
            enhanced_entry["logger"] = base_log_entry.get(
                "logger", "omnibase.logger_node"
            )
            enhanced_entry["version"] = base_log_entry.get("version", "1.0.0")

        return enhanced_entry

    def _format_message(self, message: str) -> str:
        """
        Format the log message based on configuration.

        Args:
            message: Original message

        Returns:
            Formatted message
        """
        if not message:
            return ""

        # Apply truncation if configured
        if self.format_settings.get("truncate_long_messages", False) and len(
            message
        ) > self.format_settings.get("max_message_length", 1000):

            max_length = self.format_settings.get("max_message_length", 1000)
            return message[: max_length - 3] + "..."

        return message

    def _format_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format context data based on configuration.

        Args:
            context: Original context dictionary

        Returns:
            Formatted context dictionary
        """
        if not context:
            return {}

        max_depth = self.format_settings.get("max_context_depth", 3)
        return self._truncate_dict_depth(context, max_depth)

    def _truncate_dict_depth(
        self, data: Any, max_depth: int, current_depth: int = 0
    ) -> Dict[str, Any]:
        """
        Recursively truncate dictionary depth.

        Args:
            data: Data to truncate
            max_depth: Maximum allowed depth
            current_depth: Current recursion depth

        Returns:
            Truncated data as a dictionary
        """
        if current_depth >= max_depth:
            return {"truncated": f"<truncated at depth {max_depth}>"}

        if isinstance(data, dict):
            return {
                key: (
                    self._truncate_dict_depth(value, max_depth, current_depth + 1)
                    if isinstance(value, (dict, list))
                    else value
                )
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return {
                f"item_{i}": (
                    self._truncate_dict_depth(item, max_depth, current_depth + 1)
                    if isinstance(item, (dict, list))
                    else item
                )
                for i, item in enumerate(data)
            }
        else:
            return {"value": data}


def create_output_handler(
    config: Optional[LoggerOutputConfig] = None,
) -> ContextAwareOutputHandler:
    """
    Create a context-aware output handler.

    Args:
        config: Logger output configuration (creates default if None)

    Returns:
        ContextAwareOutputHandler instance
    """
    if config is None:
        from ..models.logger_output_config import create_default_config

        config = create_default_config()

    return ContextAwareOutputHandler(config)


def create_log_formatter(
    config: Optional[LoggerOutputConfig] = None,
) -> EnhancedLogFormatter:
    """
    Create an enhanced log formatter.

    Args:
        config: Logger output configuration (creates default if None)

    Returns:
        EnhancedLogFormatter instance
    """
    if config is None:
        from ..models.logger_output_config import create_default_config

        config = create_default_config()

    return EnhancedLogFormatter(config)
