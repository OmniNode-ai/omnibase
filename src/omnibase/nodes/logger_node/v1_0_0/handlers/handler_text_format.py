# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_text_format.py
# version: 1.0.0
# uuid: a94c3d43-2a54-4fb5-82eb-7a42743b71cb
# author: OmniNode Team
# created_at: 2025-05-26T12:14:15.146081
# last_modified_at: 2025-05-26T16:53:38.735957
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 59f0a5c44238e87e33d053efa62f50e120da8e802e5c007a50c191214aff3fa1
# entrypoint: python@handler_text_format.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_text_format
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Text format handler for the logger node.

This handler provides plain text formatting capabilities for log entries,
implementing the ProtocolLogFormatHandler interface with customizable
formatting templates and human-readable output.
"""

from datetime import datetime
from typing import Any, Dict, List

from omnibase.core.error_codes import CoreErrorCode, OnexError

from ..models.state import LoggerInputState
from ..protocol.protocol_log_format_handler import ProtocolLogFormatHandler


class TextFormatHandler(ProtocolLogFormatHandler):
    """
    Text format handler for log entries.

    Provides human-readable plain text formatting with customizable templates
    and structured field presentation. No external dependencies required.
    """

    # Handler metadata properties
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "text_format_handler"

    @property
    def handler_version(self) -> str:
        """Version of this handler implementation."""
        return "1.0.0"

    @property
    def handler_author(self) -> str:
        """Author or team responsible for this handler."""
        return "OmniNode Team"

    @property
    def handler_description(self) -> str:
        """Brief description of what this handler does."""
        return "Formats log entries as human-readable plain text with customizable templates"

    @property
    def supported_formats(self) -> List[str]:
        """List of output formats this handler supports."""
        return ["text", "txt"]

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 100  # Core handler priority

    @property
    def requires_dependencies(self) -> List[str]:
        """List of optional dependencies required by this handler."""
        return []  # No external dependencies

    # Core handler methods
    def can_handle(self, format_name: str) -> bool:
        """Return True if this handler can process the given format."""
        return format_name.lower() in [f.lower() for f in self.supported_formats]

    def format_log_entry(
        self, input_state: LoggerInputState, log_entry: Dict[str, Any]
    ) -> str:
        """
        Format a log entry as plain text.

        Args:
            input_state: Logger input state containing configuration
            log_entry: Base log entry structure with timestamp, level, message, etc.

        Returns:
            Formatted log entry as plain text string

        Raises:
            OnexError: If text formatting fails
        """
        try:
            lines = []

            # Format timestamp if present
            if "timestamp" in log_entry:
                timestamp = log_entry["timestamp"]
                if isinstance(timestamp, str):
                    lines.append(f"Time: {timestamp}")
                elif isinstance(timestamp, datetime):
                    lines.append(f"Time: {timestamp.isoformat()}")
                else:
                    lines.append(f"Time: {str(timestamp)}")

            # Format level if present
            if "level" in log_entry:
                lines.append(f"Level: {log_entry['level']}")

            # Format message if present
            if "message" in log_entry:
                lines.append(f"Message: {log_entry['message']}")

            # Format correlation ID if present
            if "correlation_id" in log_entry:
                lines.append(f"Correlation ID: {log_entry['correlation_id']}")

            # Format additional fields
            excluded_fields = {"timestamp", "level", "message", "correlation_id"}
            for key, value in log_entry.items():
                if key not in excluded_fields:
                    if isinstance(value, (dict, list)):
                        lines.append(f"{key.title()}:")
                        lines.append(f"  {self._format_complex_value(value, indent=2)}")
                    else:
                        lines.append(f"{key.title()}: {value}")

            return "\n".join(lines)

        except Exception as exc:
            raise OnexError(
                f"Failed to format log entry as text: {str(exc)}",
                CoreErrorCode.INVALID_PARAMETER,
            )

    def _format_complex_value(self, value: Any, indent: int = 0) -> str:
        """Format complex values (dicts, lists) with proper indentation."""
        indent_str = " " * indent

        if isinstance(value, dict):
            lines = []
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{indent_str}{k}:")
                    lines.append(self._format_complex_value(v, indent + 2))
                else:
                    lines.append(f"{indent_str}{k}: {v}")
            return "\n".join(lines)

        elif isinstance(value, list):
            lines = []
            for item in value:
                if isinstance(item, (dict, list)):
                    lines.append(
                        f"{indent_str}- {self._format_complex_value(item, indent + 2)}"
                    )
                else:
                    lines.append(f"{indent_str}- {item}")
            return "\n".join(lines)

        else:
            return f"{indent_str}{value}"

    def validate_dependencies(self) -> bool:
        """
        Validate that all required dependencies are available.

        Returns:
            True (no external dependencies required)
        """
        return True

    def get_format_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this format handler.

        Returns:
            Dictionary containing text format metadata
        """
        return {
            "format_name": "text",
            "file_extensions": [".txt", ".log"],
            "mime_types": ["text/plain"],
            "description": "Plain text format - human-readable unstructured text",
            "features": [
                "human_readable",
                "simple_format",
                "no_escaping_needed",
                "customizable_templates",
            ],
            "use_cases": [
                "human_readable_logs",
                "console_output",
                "simple_debugging",
                "legacy_systems",
            ],
            "output_characteristics": {
                "human_readable": True,
                "machine_parseable": False,
                "compact": True,
                "preserves_types": False,
            },
        }
