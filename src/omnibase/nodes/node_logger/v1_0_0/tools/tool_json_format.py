# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.988941'
# description: Stamped by PythonHandler
# entrypoint: python://handler_json_format
# hash: 412a0246986b53ed9fd7100bda290447160dec87bf65f272014081c33dee97f8
# last_modified_at: '2025-05-29T14:13:59.164782+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: handler_json_format.py
# namespace: python://omnibase.nodes.logger_node.v1_0_0.handlers.handler_json_format
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: f0d5e1e8-b796-4700-914e-8fac15e17852
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
JSON format handler for the logger node.

This handler provides JSON formatting capabilities for log entries,
implementing the ProtocolLogFormatHandler interface with proper
metadata and dependency management.
"""

import json
from typing import Any, Dict, List

from omnibase.core.core_error_codes import CoreErrorCode, OnexError

from ..models.state import LoggerInputState, LoggerOutputState
from omnibase.protocol.protocol_log_format_handler import ProtocolLogFormatHandler


class ToolJsonFormat(ProtocolLogFormatHandler):
    """
    JSON format handler for log entries.

    Provides clean, structured JSON formatting with proper indentation
    and Unicode support. No external dependencies required.
    """

    # Handler metadata properties
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "json_format_handler"

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
        return "Formats log entries as clean, structured JSON with proper indentation"

    @property
    def supported_formats(self) -> List[str]:
        """List of output formats this handler supports."""
        return ["json"]

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 100  # Core handler priority

    @property
    def requires_dependencies(self) -> List[str]:
        """List of optional dependencies required by this handler."""
        return []  # JSON is built into Python

    # Core handler methods
    def can_handle(self, format_name: str) -> bool:
        """Return True if this handler can process the given format."""
        return format_name.lower() in [f.lower() for f in self.supported_formats]

    def format_log_entry(
        self, input_state: LoggerInputState, log_entry: Dict[str, Any]
    ) -> str:
        """
        Format a log entry as JSON.

        Args:
            input_state: Logger input state containing configuration
            log_entry: Base log entry structure with timestamp, level, message, etc.

        Returns:
            Formatted log entry as JSON string

        Raises:
            OnexError: If JSON serialization fails
        """
        try:
            return json.dumps(log_entry, indent=2, ensure_ascii=False)
        except (TypeError, OnexError) as exc:
            raise OnexError(
                f"Failed to serialize log entry to JSON: {str(exc)}",
                CoreErrorCode.INVALID_PARAMETER,
            )

    def validate_dependencies(self) -> bool:
        """
        Validate that all required dependencies are available.

        Returns:
            True (JSON is always available in Python)
        """
        return True  # JSON is built into Python

    def get_format_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this format handler.

        Returns:
            Dictionary containing JSON format metadata
        """
        return {
            "format_name": "json",
            "file_extensions": [".json"],
            "mime_types": ["application/json"],
            "description": "JavaScript Object Notation - structured data format",
            "features": [
                "structured_data",
                "unicode_support",
                "nested_objects",
                "arrays",
                "null_values",
            ],
            "use_cases": [
                "api_logging",
                "structured_logging",
                "machine_readable_logs",
                "log_aggregation",
            ],
            "output_characteristics": {
                "human_readable": True,
                "machine_parseable": True,
                "compact": False,
                "preserves_types": True,
            },
        }
