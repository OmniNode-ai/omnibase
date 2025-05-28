# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_yaml_format.py
# version: 1.0.0
# uuid: 5ad407bd-1b7b-445b-9be3-30e55a51da5a
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.018377
# last_modified_at: 2025-05-28T17:20:05.585278
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 883018f21ceac16e837f9e9f535863966fcdf34520c2041efbc9b6ab0dde2d76
# entrypoint: python@handler_yaml_format.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.handler_yaml_format
# meta_type: tool
# === /OmniNode:Metadata ===


"""
YAML format handler for the logger node.

This handler provides YAML formatting capabilities for log entries,
implementing the ProtocolLogFormatHandler interface with proper
metadata and dependency management. Includes fallback formatting
when PyYAML is not available.
"""

from typing import Any, Dict, List

from omnibase.core.core_error_codes import CoreErrorCode, OnexError

from ..models.state import LoggerInputState
from ..protocol.protocol_log_format_handler import ProtocolLogFormatHandler


class YamlFormatHandler(ProtocolLogFormatHandler):
    """
    YAML format handler for log entries.

    Provides clean, human-readable YAML formatting with proper indentation
    and Unicode support. Falls back to manual formatting if PyYAML is not available.
    """

    # Handler metadata properties
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "yaml_format_handler"

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
        return "Formats log entries as human-readable YAML with fallback support"

    @property
    def supported_formats(self) -> List[str]:
        """List of output formats this handler supports."""
        return ["yaml", "yml"]

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 100  # Core handler priority

    @property
    def requires_dependencies(self) -> List[str]:
        """List of optional dependencies required by this handler."""
        return ["yaml"]  # PyYAML is optional, fallback available

    # Core handler methods
    def can_handle(self, format_name: str) -> bool:
        """Return True if this handler can process the given format."""
        return format_name.lower() in [f.lower() for f in self.supported_formats]

    def format_log_entry(
        self, input_state: LoggerInputState, log_entry: Dict[str, Any]
    ) -> str:
        """
        Format a log entry as YAML.

        Args:
            input_state: Logger input state containing configuration
            log_entry: Base log entry structure with timestamp, level, message, etc.

        Returns:
            Formatted log entry as YAML string

        Raises:
            OnexError: If YAML serialization fails
        """
        try:
            # Try to use PyYAML if available
            try:
                import yaml

                return yaml.dump(
                    log_entry, default_flow_style=False, allow_unicode=True
                )
            except ImportError:
                # Fallback to manual YAML formatting
                return self._format_yaml_manual(log_entry)
        except Exception as exc:
            raise OnexError(
                f"Failed to serialize log entry to YAML: {str(exc)}",
                CoreErrorCode.INVALID_PARAMETER,
            )

    def _format_yaml_manual(self, log_entry: Dict[str, Any]) -> str:
        """Manual YAML formatting fallback when PyYAML is not available."""
        lines = []
        for key, value in log_entry.items():
            if isinstance(value, str):
                # Escape quotes and handle multiline strings
                if "\n" in value or '"' in value:
                    lines.append(f"{key}: |")
                    for line in value.split("\n"):
                        lines.append(f"  {line}")
                else:
                    lines.append(f'{key}: "{value}"')
            elif isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    if isinstance(item, str):
                        lines.append(f'  - "{item}"')
                    else:
                        lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, str):
                        lines.append(f'  {subkey}: "{subvalue}"')
                    else:
                        lines.append(f"  {subkey}: {subvalue}")
            elif value is None:
                lines.append(f"{key}: null")
            elif isinstance(value, bool):
                lines.append(f"{key}: {str(value).lower()}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def validate_dependencies(self) -> bool:
        """
        Validate that all required dependencies are available.

        Returns:
            True (fallback formatting always available)
        """
        # Always return True since we have fallback formatting
        return True

    def get_format_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this format handler.

        Returns:
            Dictionary containing YAML format metadata
        """
        # Check if PyYAML is available
        yaml_available = False
        try:
            import yaml  # noqa: F401

            yaml_available = True
        except ImportError:
            pass

        return {
            "format_name": "yaml",
            "file_extensions": [".yaml", ".yml"],
            "mime_types": ["application/x-yaml", "text/yaml"],
            "description": "YAML Ain't Markup Language - human-readable data serialization",
            "features": [
                "human_readable",
                "structured_data",
                "unicode_support",
                "multiline_strings",
                "comments_support" if yaml_available else "basic_formatting",
            ],
            "use_cases": [
                "configuration_logging",
                "human_readable_logs",
                "development_debugging",
                "documentation",
            ],
            "output_characteristics": {
                "human_readable": True,
                "machine_parseable": True,
                "compact": False,
                "preserves_types": yaml_available,
            },
            "dependencies": {
                "pyyaml_available": yaml_available,
                "fallback_formatting": True,
            },
        }
