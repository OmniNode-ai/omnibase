"""
Protocol for Context-Aware Output Handler in ONEX logger node.

Defines the interface for outputting formatted log entries to various destinations.
"""
from typing import Protocol

class ProtocolContextAwareOutputHandler(Protocol):
    """
    Protocol for context-aware output handler.
    Implementations must provide output routing for formatted log entries.
    """
    def output_log_entry(self, formatted_log: str, log_level: str) -> None:
        """
        Output a formatted log entry to configured destinations.
        Args:
            formatted_log: The formatted log entry string
            log_level: Log level for routing decisions (error -> stderr)
        """
        ...

    def close(self) -> None:
        """
        Close any open file handles or resources.
        """
        ... 