# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_markdown_format.py
# version: 1.0.0
# uuid: 30c33eed-90f1-413d-be88-ea9294d13e3d
# author: OmniNode Team
# created_at: 2025-05-26T12:14:43.236679
# last_modified_at: 2025-05-26T16:53:38.718337
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 89b01a1f5f5cc99a06d39f34c7699fe266b0f79bbcc8e8c3e806f032f15eac5b
# entrypoint: python@handler_markdown_format.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_markdown_format
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Markdown format handler for the logger node.

This handler provides Markdown formatting capabilities for log entries,
implementing the ProtocolLogFormatHandler interface with structured
documentation-style output and proper escaping.
"""

from datetime import datetime
from typing import Any, Dict, List

from omnibase.core.core_error_codes import CoreErrorCode, OnexError

from ..models.state import LoggerInputState
from ..protocol.protocol_log_format_handler import ProtocolLogFormatHandler


class MarkdownFormatHandler(ProtocolLogFormatHandler):
    """
    Markdown format handler for log entries.

    Provides structured Markdown formatting with proper escaping, headers,
    and documentation-style presentation. No external dependencies required.
    """

    # Handler metadata properties
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "markdown_format_handler"

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
        return "Formats log entries as structured Markdown with proper escaping and documentation style"

    @property
    def supported_formats(self) -> List[str]:
        """List of output formats this handler supports."""
        return ["markdown", "md"]

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
        Format a log entry as Markdown.

        Args:
            input_state: Logger input state containing configuration
            log_entry: Base log entry structure with timestamp, level, message, etc.

        Returns:
            Formatted log entry as Markdown string

        Raises:
            OnexError: If Markdown formatting fails
        """
        try:
            lines = []

            # Add main header
            level = log_entry.get("level", "LOG")
            timestamp = log_entry.get("timestamp", "")
            if timestamp:
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.isoformat()
                lines.append(f"## {level} Entry - {timestamp}")
            else:
                lines.append(f"## {level} Entry")

            lines.append("")  # Empty line after header

            # Format message if present
            if "message" in log_entry:
                lines.append("### Message")
                lines.append("")
                message = self._escape_markdown(str(log_entry["message"]))
                lines.append(message)
                lines.append("")

            # Format correlation ID if present
            if "correlation_id" in log_entry:
                lines.append("### Correlation ID")
                lines.append("")
                lines.append(f"`{log_entry['correlation_id']}`")
                lines.append("")

            # Format additional fields
            excluded_fields = {"timestamp", "level", "message", "correlation_id"}
            additional_fields = {
                k: v for k, v in log_entry.items() if k not in excluded_fields
            }

            if additional_fields:
                lines.append("### Additional Fields")
                lines.append("")

                for key, value in additional_fields.items():
                    lines.append(f"**{key.title()}:**")
                    lines.append("")

                    if isinstance(value, (dict, list)):
                        lines.append("```json")
                        import json

                        lines.append(json.dumps(value, indent=2))
                        lines.append("```")
                    else:
                        escaped_value = self._escape_markdown(str(value))
                        lines.append(escaped_value)

                    lines.append("")

            return "\n".join(lines)

        except Exception as exc:
            raise OnexError(
                f"Failed to format log entry as Markdown: {str(exc)}",
                CoreErrorCode.INVALID_PARAMETER,
            )

    def _escape_markdown(self, text: str) -> str:
        """Escape special Markdown characters in text."""
        # Escape common Markdown special characters
        special_chars = [
            "\\",
            "`",
            "*",
            "_",
            "{",
            "}",
            "[",
            "]",
            "(",
            ")",
            "#",
            "+",
            "-",
            ".",
            "!",
        ]

        for char in special_chars:
            text = text.replace(char, f"\\{char}")

        return text

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
            Dictionary containing Markdown format metadata
        """
        return {
            "format_name": "markdown",
            "file_extensions": [".md", ".markdown"],
            "mime_types": ["text/markdown", "text/x-markdown"],
            "description": "Markdown - structured text format with formatting syntax",
            "features": [
                "human_readable",
                "structured_formatting",
                "documentation_style",
                "proper_escaping",
                "headers_and_sections",
            ],
            "use_cases": [
                "documentation_logs",
                "report_generation",
                "human_readable_reports",
                "structured_debugging",
            ],
            "output_characteristics": {
                "human_readable": True,
                "machine_parseable": True,
                "compact": False,
                "preserves_types": False,
            },
        }
