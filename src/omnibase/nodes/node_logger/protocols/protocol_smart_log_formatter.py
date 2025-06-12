"""
Protocol for Smart Log Formatter in ONEX logger node.

Defines the interface for context-aware log event formatting with multiple output levels.
"""
from typing import Any, Dict, Optional, Protocol
from omnibase.enums import LogLevelEnum
from omnibase.model.model_log_entry import LogContextModel

class ProtocolSmartLogFormatter(Protocol):
    """
    Protocol for smart log event formatting.
    Implementations must provide context-aware formatting for log events.
    """
    def format_log_event(
        self,
        level: LogLevelEnum,
        event_type: str,
        message: str,
        context: Optional[LogContextModel] = None,
        data: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> str:
        """
        Format a log event using smart context-aware formatting.
        Args:
            level: Log level
            event_type: Type of log event
            message: Primary log message
            context: Log context model
            data: Additional structured data
            correlation_id: Correlation ID for tracing
        Returns:
            Formatted log string
        """
        ... 