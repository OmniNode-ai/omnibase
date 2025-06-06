# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_csv_format.py
# version: 1.0.0
# uuid: a6b0307f-66d5-426e-a639-cee2afa7b965
# author: OmniNode Team
# created_at: 2025-05-26T12:15:16.571982
# last_modified_at: 2025-05-26T16:53:38.716008
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: cf872e64c2509673cb30edbe253d583d63d26b217e9da5e43318ab3ad8623071
# entrypoint: python@handler_csv_format.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_csv_format
# meta_type: tool
# === /OmniNode:Metadata ===


"""
CSV format handler for the logger node.

This handler provides CSV formatting capabilities for log entries,
implementing the ProtocolLogFormatHandler interface with proper
escaping and tabular data presentation.
"""

import csv
import io
from datetime import datetime
from typing import Any, Dict, List

from omnibase.core.error_codes import CoreErrorCode, OnexError

from ..models.state import LoggerInputState
from ..protocol.protocol_log_format_handler import ProtocolLogFormatHandler


class CsvFormatHandler(ProtocolLogFormatHandler):
    """
    CSV format handler for log entries.

    Provides tabular CSV formatting with proper escaping and field ordering.
    Uses Python's built-in csv module for standards-compliant output.
    """

    # Handler metadata properties
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "csv_format_handler"

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
        return (
            "Formats log entries as CSV with proper escaping and tabular presentation"
        )

    @property
    def supported_formats(self) -> List[str]:
        """List of output formats this handler supports."""
        return ["csv"]

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 100  # Core handler priority

    @property
    def requires_dependencies(self) -> List[str]:
        """List of optional dependencies required by this handler."""
        return []  # CSV module is built into Python

    # Core handler methods
    def can_handle(self, format_name: str) -> bool:
        """Return True if this handler can process the given format."""
        return format_name.lower() in [f.lower() for f in self.supported_formats]

    def format_log_entry(
        self, input_state: LoggerInputState, log_entry: Dict[str, Any]
    ) -> str:
        """
        Format a log entry as CSV.

        Args:
            input_state: Logger input state containing configuration
            log_entry: Base log entry structure with timestamp, level, message, etc.

        Returns:
            Formatted log entry as CSV string

        Raises:
            OnexError: If CSV formatting fails
        """
        try:
            # Define standard field order for consistency
            standard_fields = ["timestamp", "level", "message", "correlation_id"]

            # Prepare the row data
            row_data = {}

            # Process standard fields first
            for field in standard_fields:
                if field in log_entry:
                    value = log_entry[field]
                    if isinstance(value, datetime):
                        row_data[field] = value.isoformat()
                    elif isinstance(value, (dict, list)):
                        # Serialize complex types as JSON strings
                        import json

                        row_data[field] = json.dumps(value)
                    else:
                        row_data[field] = str(value)
                else:
                    row_data[field] = ""

            # Add any additional fields
            for key, value in log_entry.items():
                if key not in standard_fields:
                    if isinstance(value, datetime):
                        row_data[key] = value.isoformat()
                    elif isinstance(value, (dict, list)):
                        # Serialize complex types as JSON strings
                        import json

                        row_data[key] = json.dumps(value)
                    else:
                        row_data[key] = str(value)

            # Create CSV output
            output = io.StringIO()
            fieldnames = list(row_data.keys())
            writer = csv.DictWriter(
                output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL
            )

            # Write the row (no header for individual log entries)
            writer.writerow(row_data)

            # Get the CSV string and strip the trailing newline
            csv_string = output.getvalue().rstrip("\n")
            output.close()

            return csv_string

        except Exception as exc:
            raise OnexError(
                f"Failed to format log entry as CSV: {str(exc)}",
                CoreErrorCode.INVALID_PARAMETER,
            )

    def format_log_entries_with_header(
        self, input_state: LoggerInputState, log_entries: List[Dict[str, Any]]
    ) -> str:
        """
        Format multiple log entries as CSV with header row.

        This is a convenience method for formatting multiple entries with a header.

        Args:
            input_state: Logger input state containing configuration
            log_entries: List of log entry dictionaries

        Returns:
            Formatted log entries as CSV string with header

        Raises:
            OnexError: If CSV formatting fails
        """
        try:
            if not log_entries:
                return ""

            # Collect all unique field names from all entries
            all_fields: set[str] = set()
            standard_fields = ["timestamp", "level", "message", "correlation_id"]

            for entry in log_entries:
                all_fields.update(entry.keys())

            # Order fields: standard fields first, then others alphabetically
            ordered_fields = []
            for field in standard_fields:
                if field in all_fields:
                    ordered_fields.append(field)
                    all_fields.remove(field)

            # Add remaining fields alphabetically
            ordered_fields.extend(sorted(all_fields))

            # Create CSV output
            output = io.StringIO()
            writer = csv.DictWriter(
                output, fieldnames=ordered_fields, quoting=csv.QUOTE_MINIMAL
            )

            # Write header
            writer.writeheader()

            # Write all rows
            for entry in log_entries:
                row_data = {}
                for field in ordered_fields:
                    if field in entry:
                        value = entry[field]
                        if isinstance(value, datetime):
                            row_data[field] = value.isoformat()
                        elif isinstance(value, (dict, list)):
                            import json

                            row_data[field] = json.dumps(value)
                        else:
                            row_data[field] = str(value)
                    else:
                        row_data[field] = ""

                writer.writerow(row_data)

            csv_string = output.getvalue()
            output.close()

            return csv_string

        except Exception as exc:
            raise OnexError(
                f"Failed to format log entries as CSV: {str(exc)}",
                CoreErrorCode.INVALID_PARAMETER,
            )

    def validate_dependencies(self) -> bool:
        """
        Validate that all required dependencies are available.

        Returns:
            True (CSV module is built into Python)
        """
        return True

    def get_format_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this format handler.

        Returns:
            Dictionary containing CSV format metadata
        """
        return {
            "format_name": "csv",
            "file_extensions": [".csv"],
            "mime_types": ["text/csv", "application/csv"],
            "description": "Comma-Separated Values - tabular data format",
            "features": [
                "tabular_format",
                "machine_readable",
                "spreadsheet_compatible",
                "proper_escaping",
                "field_ordering",
            ],
            "use_cases": [
                "data_analysis",
                "spreadsheet_import",
                "tabular_reports",
                "log_aggregation",
            ],
            "output_characteristics": {
                "human_readable": True,
                "machine_parseable": True,
                "compact": True,
                "preserves_types": False,
            },
        }
