"""
Protocol for Logger Node Emit Log Event functionality.

Defines the interface for structured logging services that route events through
the logger node with smart formatting and correlation tracking.

This protocol enables dependency injection and service discovery for logging
functionality across the ONEX ecosystem.
"""

from typing import Any, Dict, Optional, Protocol

from omnibase.enums import LogLevelEnum
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus


class ProtocolLoggerEmitLogEvent(Protocol):
    """
    Protocol for emit log event functionality.
    
    Defines the interface for the main entry point of ONEX structured logging.
    Implementations should route events through the logger node for centralized
    processing with smart formatting.
    """

    def emit_log_event(
        self,
        level: LogLevelEnum,
        event_type: str,
        message: str,
        node_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        event_bus: Optional[ProtocolEventBus] = None,
    ) -> None:
        """
        Emit a structured log event through the logger node.
        
        Args:
            level: Log level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)
            event_type: Type of event (function_entry, node_execution_start, etc.)
            message: Primary log message
            node_id: Node ID for context (auto-detected if not provided)
            correlation_id: Correlation ID for tracing (auto-generated if not provided)
            data: Additional structured data
            event_bus: Event bus for routing (uses default if not provided)
        """
        ...

    def emit_log_event_sync(
        self,
        level: LogLevelEnum,
        message: str,
        event_type: str = "generic",
        node_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        event_bus: Optional[ProtocolEventBus] = None,
    ) -> None:
        """
        Synchronous version of emit_log_event for compatibility.
        
        Args:
            level: Log level
            message: Log message
            event_type: Event type
            node_id: Node ID
            correlation_id: Correlation ID
            data: Additional data
            event_bus: Event bus
        """
        ...

    async def emit_log_event_async(
        self,
        level: LogLevelEnum,
        message: str,
        event_type: str = "generic",
        node_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        event_bus: Optional[ProtocolEventBus] = None,
    ) -> None:
        """
        Asynchronous version of emit_log_event.
        
        Args:
            level: Log level
            message: Log message
            event_type: Event type
            node_id: Node ID
            correlation_id: Correlation ID
            data: Additional data
            event_bus: Event bus
        """
        ...


class ProtocolLoggerDecorators(Protocol):
    """
    Protocol for logging decorators and utilities.
    
    Defines the interface for logging decorators that provide automatic
    function lifecycle logging and performance monitoring.
    """

    def trace_function_lifecycle(self, func) -> callable:
        """
        Decorator to automatically log function entry/exit with TRACE level.
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function with automatic lifecycle logging
        """
        ...

    def tool_logger_performance_metrics(self, threshold_ms: int = 1000) -> callable:
        """
        Decorator to log performance metrics for functions.
        
        Args:
            threshold_ms: Log warning if execution exceeds this threshold
            
        Returns:
            Decorator function
        """
        ...


class ProtocolLoggerCodeBlock(Protocol):
    """
    Protocol for code block logging context manager.
    
    Defines the interface for logging code block execution with automatic
    entry/exit logging and exception handling.
    """

    def __init__(
        self,
        block_name: str,
        correlation_id: Optional[str] = None,
        level: LogLevelEnum = LogLevelEnum.DEBUG,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize code block logger.
        
        Args:
            block_name: Name of the code block
            correlation_id: Correlation ID for tracing
            level: Log level for block events
            data: Additional structured data
        """
        ...

    def __enter__(self):
        """Enter the code block context."""
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the code block context."""
        ... 