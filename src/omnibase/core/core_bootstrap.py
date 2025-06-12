"""
Core Bootstrap for ONEX Service Discovery.

Provides minimal bootstrap logic to discover and access ONEX services through
the registry node. This module contains only the essential functionality needed
to bootstrap the service discovery system.

All complex functionality has been moved to service nodes following the
registry-centric architecture pattern.
"""

import os
from typing import Any, Optional, Type, TypeVar

from omnibase.enums import LogLevelEnum

# Type variable for protocol types
T = TypeVar('T')


def get_service(protocol_type: Type[T]) -> Optional[T]:
    """
    Get a service implementation for the given protocol type.
    
    This is the main entry point for service discovery in ONEX. It attempts
    to find the registry node and use it for service resolution, with fallback
    mechanisms for bootstrap scenarios.
    
    Args:
        protocol_type: The protocol interface to resolve
        
    Returns:
        Service implementation or None if not found
    """
    try:
        # Try to get service through registry node
        registry = _get_registry_node()
        if registry:
            return registry.get_service(protocol_type)
    except Exception:
        # Registry not available, try fallback
        pass
    
    # Try fallback implementations
    return _get_fallback_service(protocol_type)


def get_logging_service():
    """
    Get the logging service with special bootstrap handling.
    
    Returns:
        Logging service implementation
    """
    try:
        # Try to import from node_logger
        from omnibase.nodes.node_logger.v1_0_0.tools.tool_logger_emit_log_event import (
            emit_log_event,
            emit_log_event_sync,
            emit_log_event_async,
            trace_function_lifecycle,
            ToolLoggerCodeBlock,
            tool_logger_performance_metrics,
        )
        
        # Return a simple service object with the functions
        class LoggingService:
            emit_log_event = staticmethod(emit_log_event)
            emit_log_event_sync = staticmethod(emit_log_event_sync)
            emit_log_event_async = staticmethod(emit_log_event_async)
            trace_function_lifecycle = staticmethod(trace_function_lifecycle)
            ToolLoggerCodeBlock = ToolLoggerCodeBlock
            tool_logger_performance_metrics = staticmethod(tool_logger_performance_metrics)
        
        return LoggingService()
        
    except ImportError:
        # Fallback to minimal logging
        return _get_minimal_logging_service()


def emit_log_event(
    level: LogLevelEnum,
    event_type: str,
    message: str,
    **kwargs
) -> None:
    """
    Bootstrap emit_log_event function.
    
    Routes to the appropriate logging service or provides fallback.
    """
    try:
        logging_service = get_logging_service()
        if hasattr(logging_service, 'emit_log_event'):
            return logging_service.emit_log_event(level, event_type, message, **kwargs)
    except Exception:
        pass
    
    # Fallback to simple print
    print(f"[{level.name}] {message}")


def emit_log_event_sync(
    level: LogLevelEnum,
    message: str,
    event_type: str = "generic",
    **kwargs
) -> None:
    """
    Bootstrap emit_log_event_sync function.
    
    Routes to the appropriate logging service or provides fallback.
    """
    try:
        logging_service = get_logging_service()
        if hasattr(logging_service, 'emit_log_event_sync'):
            return logging_service.emit_log_event_sync(level, message, event_type, **kwargs)
    except Exception:
        pass
    
    # Fallback to simple print
    print(f"[{level.name}] {message}")


# Private helper functions

def _get_registry_node():
    """
    Attempt to find and return the registry node.
    
    Returns:
        Registry node instance or None if not found
    """
    try:
        # Try to import registry node
        from omnibase.nodes.node_registry_node.v1_0_0.node import NodeRegistryNode
        
        # Try to get existing instance or create new one
        # This is a simplified bootstrap - in production this would be more sophisticated
        return NodeRegistryNode()
        
    except ImportError:
        # Registry node not available
        return None


def _get_fallback_service(protocol_type: Type[T]) -> Optional[T]:
    """
    Get fallback service implementation for bootstrap scenarios.
    
    Args:
        protocol_type: The protocol interface to resolve
        
    Returns:
        Fallback service implementation or None
    """
    # Check if this is a logging protocol
    if hasattr(protocol_type, '__name__') and 'Logger' in protocol_type.__name__:
        return _get_minimal_logging_service()
    
    # No fallback available
    return None


def _get_minimal_logging_service():
    """
    Get minimal logging service for bootstrap scenarios.
    
    Returns:
        Minimal logging service implementation
    """
    class MinimalLoggingService:
        @staticmethod
        def emit_log_event(level, event_type, message, **kwargs):
            print(f"[{level.name}] {message}")
        
        @staticmethod
        def emit_log_event_sync(level, message, event_type="generic", **kwargs):
            print(f"[{level.name}] {message}")
        
        @staticmethod
        async def emit_log_event_async(level, message, event_type="generic", **kwargs):
            print(f"[{level.name}] {message}")
        
        @staticmethod
        def trace_function_lifecycle(func):
            # No-op decorator for bootstrap
            return func
        
        class ToolLoggerCodeBlock:
            def __init__(self, *args, **kwargs):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        
        @staticmethod
        def tool_logger_performance_metrics(threshold_ms=1000):
            def decorator(func):
                return func
            return decorator
    
    return MinimalLoggingService()


def is_service_available(protocol_type: Type[T]) -> bool:
    """
    Check if a service is available for the given protocol type.
    
    Args:
        protocol_type: The protocol interface to check
        
    Returns:
        True if service is available, False otherwise
    """
    return get_service(protocol_type) is not None


def get_available_services() -> list:
    """
    Get list of available services.
    
    Returns:
        List of available service types
    """
    try:
        registry = _get_registry_node()
        if registry and hasattr(registry, 'list_services'):
            return registry.list_services()
    except Exception:
        pass
    
    # Return minimal list for bootstrap
    return ['logging'] 