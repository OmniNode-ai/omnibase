"""
Protocol for Logger Engine in ONEX logger node.

Defines the interface for formatting and outputting log entries using pluggable format handlers.
"""
from typing import Protocol
from omnibase.nodes.node_logger.v1_0_0.models.state import LoggerInputState

class ProtocolLoggerEngine(Protocol):
    """
    Protocol for logger engine.
    Implementations must provide log entry formatting and output methods.
    """
    def format_log_entry(self, input_state: LoggerInputState) -> str:
        """
        Format a log entry using the appropriate format handler.
        Args:
            input_state: Logger input state containing message, level, format, etc.
        Returns:
            Formatted log entry as a string
        """
        ...

    def format_and_output_log_entry(self, input_state: LoggerInputState) -> str:
        """
        Format and output a log entry to configured destinations.
        Args:
            input_state: Logger input state containing message, level, format, etc.
        Returns:
            Formatted log entry as a string (same as format_log_entry)
        """
        ... 