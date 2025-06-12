"""
Core emit_log_event utility for ONEX structured logging.

This module provides the main entry point for all ONEX logging, routing
events through the logger node with smart formatting and correlation tracking.

All internal ONEX logging should use emit_log_event() instead of print() or
Python's logging module to maintain architectural purity and centralized processing.
"""

import inspect
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from omnibase.enums import LogLevelEnum
from omnibase.model.model_log_entry import LogContextModel
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus


def emit_log_event(
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
    
    This is the main entry point for all ONEX logging. Routes events through
    the logger node for centralized processing with smart formatting.
    
    Args:
        level: Log level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)
        event_type: Type of event (function_entry, node_execution_start, etc.)
        message: Primary log message
        node_id: Node ID for context (auto-detected if not provided)
        correlation_id: Correlation ID for tracing (auto-generated if not provided)
        data: Additional structured data
        event_bus: Event bus for routing (uses default if not provided)
    """
    # Auto-generate correlation ID if not provided
    if correlation_id is None:
        correlation_id = _get_or_generate_correlation_id()
    
    # Auto-detect node ID from calling context if not provided
    if node_id is None:
        node_id = _detect_node_id_from_context()
    
    # Create log context from calling frame
    context = _create_log_context_from_frame()
    
    # Get or create event bus
    if event_bus is None:
        event_bus = _get_default_event_bus()
    
    # Route through logger node
    _route_to_logger_node(
        level=level,
        event_type=event_type,
        message=message,
        node_id=node_id,
        correlation_id=correlation_id,
        context=context,
        data=data or {},
        event_bus=event_bus,
    )


def emit_log_event_sync(
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
    emit_log_event(
        level=level,
        event_type=event_type,
        message=message,
        node_id=node_id,
        correlation_id=correlation_id,
        data=data,
        event_bus=event_bus,
    )


async def emit_log_event_async(
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
    # For now, delegate to sync version
    # TODO: Implement true async routing when logger node supports it
    emit_log_event(
        level=level,
        event_type=event_type,
        message=message,
        node_id=node_id,
        correlation_id=correlation_id,
        data=data,
        event_bus=event_bus,
    )


def trace_function_lifecycle(func):
    """
    Decorator to automatically log function entry/exit with TRACE level.
    
    Usage:
        @trace_function_lifecycle
        def my_function(arg1, arg2):
            return result
    """
    def wrapper(*args, **kwargs):
        function_name = func.__name__
        module_name = func.__module__
        correlation_id = _get_or_generate_correlation_id()
        
        # Log function entry
        emit_log_event(
            level=LogLevelEnum.TRACE,
            event_type="function_entry",
            message=f"Entering {function_name}",
            correlation_id=correlation_id,
            data={
                "function": function_name,
                "module": module_name,
                "args_count": len(args),
                "kwargs_count": len(kwargs),
            }
        )
        
        start_time = datetime.utcnow()
        try:
            result = func(*args, **kwargs)
            
            # Log successful exit
            end_time = datetime.utcnow()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000
            
            emit_log_event(
                level=LogLevelEnum.TRACE,
                event_type="function_exit",
                message=f"Exiting {function_name}",
                correlation_id=correlation_id,
                data={
                    "function": function_name,
                    "module": module_name,
                    "execution_time_ms": execution_time_ms,
                    "success": True,
                }
            )
            
            return result
            
        except Exception as e:
            # Log exception exit
            end_time = datetime.utcnow()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000
            
            emit_log_event(
                level=LogLevelEnum.TRACE,
                event_type="function_exception",
                message=f"Exception in {function_name}: {str(e)}",
                correlation_id=correlation_id,
                data={
                    "function": function_name,
                    "module": module_name,
                    "execution_time_ms": execution_time_ms,
                    "success": False,
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                }
            )
            
            raise
    
    return wrapper


class log_code_block:
    """
    Context manager for logging code block execution.
    
    Usage:
        with log_code_block("processing_data", correlation_id="abc123"):
            # code block
            pass
    """
    
    def __init__(
        self,
        block_name: str,
        correlation_id: Optional[str] = None,
        level: LogLevelEnum = LogLevelEnum.DEBUG,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.block_name = block_name
        self.correlation_id = correlation_id or _get_or_generate_correlation_id()
        self.level = level
        self.data = data or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        
        emit_log_event(
            level=self.level,
            event_type="code_block_entry",
            message=f"Entering code block: {self.block_name}",
            correlation_id=self.correlation_id,
            data={
                "block_name": self.block_name,
                **self.data,
            }
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.utcnow()
        execution_time_ms = (end_time - self.start_time).total_seconds() * 1000
        
        if exc_type is None:
            # Successful completion
            emit_log_event(
                level=self.level,
                event_type="code_block_exit",
                message=f"Exiting code block: {self.block_name}",
                correlation_id=self.correlation_id,
                data={
                    "block_name": self.block_name,
                    "execution_time_ms": execution_time_ms,
                    "success": True,
                    **self.data,
                }
            )
        else:
            # Exception occurred
            emit_log_event(
                level=LogLevelEnum.ERROR,
                event_type="code_block_exception",
                message=f"Exception in code block {self.block_name}: {str(exc_val)}",
                correlation_id=self.correlation_id,
                data={
                    "block_name": self.block_name,
                    "execution_time_ms": execution_time_ms,
                    "success": False,
                    "exception_type": exc_type.__name__ if exc_type else None,
                    "exception_message": str(exc_val) if exc_val else None,
                    **self.data,
                }
            )


def log_performance_metrics(threshold_ms: int = 1000):
    """
    Decorator to log performance metrics for functions.
    
    Args:
        threshold_ms: Log warning if execution exceeds this threshold
    
    Usage:
        @log_performance_metrics(threshold_ms=500)
        def slow_function():
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            function_name = func.__name__
            correlation_id = _get_or_generate_correlation_id()
            
            start_time = datetime.utcnow()
            result = func(*args, **kwargs)
            end_time = datetime.utcnow()
            
            execution_time_ms = (end_time - start_time).total_seconds() * 1000
            
            if execution_time_ms > threshold_ms:
                emit_log_event(
                    level=LogLevelEnum.WARNING,
                    event_type="performance_threshold_exceeded",
                    message=f"Function {function_name} exceeded performance threshold",
                    correlation_id=correlation_id,
                    data={
                        "function": function_name,
                        "execution_time_ms": execution_time_ms,
                        "threshold_ms": threshold_ms,
                        "operation_name": function_name,
                    }
                )
            else:
                emit_log_event(
                    level=LogLevelEnum.DEBUG,
                    event_type="performance_metrics",
                    message=f"Function {function_name} performance metrics",
                    correlation_id=correlation_id,
                    data={
                        "function": function_name,
                        "execution_time_ms": execution_time_ms,
                        "threshold_ms": threshold_ms,
                        "operation_name": function_name,
                    }
                )
            
            return result
        
        return wrapper
    
    return decorator


# Private helper functions

def _get_or_generate_correlation_id() -> str:
    """Get correlation ID from context or generate a new one."""
    # Try to get from thread-local storage or environment
    correlation_id = os.getenv("ONEX_CORRELATION_ID")
    if correlation_id:
        return correlation_id
    
    # Generate new correlation ID
    return str(uuid.uuid4())[:8]


def _detect_node_id_from_context() -> str:
    """Detect node ID from calling context."""
    frame = inspect.currentframe()
    try:
        # Walk up the stack to find a node context
        while frame:
            frame = frame.f_back
            if frame and 'self' in frame.f_locals:
                obj = frame.f_locals['self']
                if hasattr(obj, 'node_id'):
                    return obj.node_id
                elif hasattr(obj, '__class__') and 'node' in obj.__class__.__name__.lower():
                    return obj.__class__.__name__
        
        # Fallback to module name
        caller_frame = inspect.currentframe().f_back.f_back
        if caller_frame:
            module_name = caller_frame.f_globals.get('__name__', 'unknown')
            return module_name.split('.')[-1]
        
        return "unknown"
    finally:
        del frame


def _create_log_context_from_frame() -> LogContextModel:
    """Create log context from the calling frame."""
    frame = inspect.currentframe().f_back.f_back
    
    if frame:
        return LogContextModel(
            calling_function=frame.f_code.co_name,
            calling_module=frame.f_globals.get('__name__', 'unknown'),
            calling_line=frame.f_lineno,
            node_id=_detect_node_id_from_context(),
        )
    else:
        return LogContextModel(
            calling_function="unknown",
            calling_module="unknown", 
            calling_line=0,
            node_id="unknown",
        )


def _get_default_event_bus() -> Optional[ProtocolEventBus]:
    """Get the default event bus for logging."""
    try:
        from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
        return get_event_bus()
    except ImportError:
        # Fallback to None - logger node will handle this
        return None


def _route_to_logger_node(
    level: LogLevelEnum,
    event_type: str,
    message: str,
    node_id: str,
    correlation_id: str,
    context: LogContextModel,
    data: Dict[str, Any],
    event_bus: Optional[ProtocolEventBus],
) -> None:
    """
    Route log event to logger node for processing.
    
    This function handles the actual routing of log events to the logger node
    with smart formatting and output handling.
    """
    try:
        # Import logger node components
        from omnibase.nodes.node_logger.v1_0_0.tools.tool_smart_log_formatter import (
            ToolSmartLogFormatter,
            create_smart_formatter,
        )
        from omnibase.nodes.node_logger.v1_0_0.tools.tool_context_aware_output_handler import (
            ToolContextAwareOutputHandler,
        )
        from omnibase.nodes.node_logger.v1_0_0.models.logger_output_config import (
            LoggerOutputConfig,
            create_default_config,
        )
        
        # Create formatter and output handler
        config = create_default_config()
        formatter = create_smart_formatter(config)
        output_handler = ToolContextAwareOutputHandler(config)
        
        # Format the log event
        formatted_log = formatter.format_log_event(
            level=level,
            event_type=event_type,
            message=message,
            context=context,
            data=data,
            correlation_id=correlation_id,
        )
        
        # Output the formatted log
        output_handler.output_log_entry(formatted_log, level.name)
        
    except Exception as e:
        # Fallback to simple output if logger node routing fails
        fallback_message = f"[{level.name}] {message} [{correlation_id}] (logger routing failed: {str(e)})"
        print(fallback_message) 