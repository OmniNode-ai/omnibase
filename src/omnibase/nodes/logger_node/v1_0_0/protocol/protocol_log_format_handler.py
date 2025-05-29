# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.149166'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_log_format_handler.py
# hash: f0ae95341330dc84141128c153e52e267082cff49e37a277fd6ccd17b879f73b
# last_modified_at: '2025-05-29T11:50:11.353837+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_log_format_handler.py
# namespace: omnibase.protocol_log_format_handler
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 10ed3ed0-4cba-40d3-837f-41854d2a1a64
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Protocol for pluggable log format handlers in the logger node.

This protocol defines the interface that all log format handlers must implement
to provide consistent, extensible formatting capabilities for different output
formats (JSON, YAML, Markdown, Text, CSV, etc.).

Following the established ONEX architecture patterns for pluggable handlers.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Protocol, runtime_checkable

from ..models.state import LoggerInputState


@runtime_checkable
class ProtocolLogFormatHandler(Protocol):
    """
    Protocol for log format handlers in the logger node.

    Each handler is responsible for formatting log entries in a specific output
    format (JSON, YAML, Markdown, Text, CSV, etc.). Handlers must be stateless
    and thread-safe.

    All handlers must declare metadata properties for introspection and plugin
    management, following the established ONEX handler architecture.
    """

    # Required metadata properties for handler introspection
    @property
    @abstractmethod
    def handler_name(self) -> str:
        """Unique name for this handler (e.g., 'json_format_handler', 'yaml_format_handler')."""
        ...

    @property
    @abstractmethod
    def handler_version(self) -> str:
        """Version of this handler implementation (e.g., '1.0.0')."""
        ...

    @property
    @abstractmethod
    def handler_author(self) -> str:
        """Author or team responsible for this handler (e.g., 'OmniNode Team')."""
        ...

    @property
    @abstractmethod
    def handler_description(self) -> str:
        """Brief description of what this handler does."""
        ...

    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """List of output formats this handler supports (e.g., ['json'], ['yaml', 'yml'])."""
        ...

    @property
    @abstractmethod
    def handler_priority(self) -> int:
        """Default priority for this handler (higher wins conflicts). Core=100, Runtime=50, Node-local=10, Plugin=0."""
        ...

    @property
    @abstractmethod
    def requires_dependencies(self) -> List[str]:
        """List of optional dependencies required by this handler (e.g., ['yaml', 'csv'])."""
        ...

    # Core handler methods
    @abstractmethod
    def can_handle(self, format_name: str) -> bool:
        """Return True if this handler can process the given format."""
        ...

    @abstractmethod
    def format_log_entry(
        self, input_state: LoggerInputState, log_entry: Dict[str, Any]
    ) -> str:
        """
        Format a log entry according to this handler's output format.

        Args:
            input_state: Logger input state containing configuration and context
            log_entry: Base log entry structure with timestamp, level, message, etc.

        Returns:
            Formatted log entry as a string

        Raises:
            OnexError: If formatting fails or dependencies are missing
        """
        ...

    @abstractmethod
    def validate_dependencies(self) -> bool:
        """
        Validate that all required dependencies are available.

        Returns:
            True if all dependencies are available, False otherwise
        """
        ...

    @abstractmethod
    def get_format_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this format handler.

        Returns:
            Dictionary containing format-specific metadata like file extensions,
            MIME types, typical use cases, etc.
        """
        ...
