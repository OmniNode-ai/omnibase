"""
Core Logging Protocol for Bootstrap.

Minimal protocol definition for logging services used during bootstrap
and service discovery. The full implementation resides in node_logger.

This protocol enables core modules to request logging services without
creating circular dependencies.
"""

from typing import Any, Dict, Optional, Protocol

from omnibase.enums import LogLevelEnum


class ProtocolCoreLogging(Protocol):
    """
    Minimal logging protocol for core bootstrap scenarios.
    
    This protocol defines the essential logging interface needed during
    system bootstrap before the full node_logger service is available.
    """

    def emit_log_event_sync(
        self,
        level: LogLevelEnum,
        message: str,
        event_type: str = "generic",
        node_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """
        Emit a structured log event synchronously.
        
        Args:
            level: Log level
            message: Log message
            event_type: Event type
            node_id: Node ID
            correlation_id: Correlation ID
            data: Additional data
            **kwargs: Additional arguments
        """
        ...

    def trace_function_lifecycle(self, func) -> callable:
        """
        Decorator for function lifecycle logging.
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function
        """
        ... 