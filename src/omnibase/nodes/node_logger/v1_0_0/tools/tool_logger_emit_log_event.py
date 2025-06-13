# === OmniNode:Metadata ===
# author: OmniNode Team
# description: Canonical emit_log_event tool for ONEX logger node
# === /OmniNode:Metadata ===

"""
Structured logging emit functions for ONEX logger node.

Implements protocol-compliant, registry-driven logging utilities:
- emit_log_event
- emit_log_event_sync
- emit_log_event_async
- trace_function_lifecycle
- ToolLoggerCodeBlock (context manager)
- tool_logger_performance_metrics (decorator)

All dependencies must be resolved via registry injection. No direct core/runtime imports except for protocol interfaces.
"""

import os
import uuid
import inspect
from datetime import datetime
from typing import Any, Dict, Optional, Callable, Type

from omnibase.enums.log_level import LogLevelEnum
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.model.model_log_entry import LogContextModel
from .tool_smart_log_formatter import ToolSmartLogFormatter, create_smart_formatter
from .tool_context_aware_output_handler import ToolContextAwareOutputHandler
from ..models.logger_output_config import LoggerOutputConfig, create_default_config
from omnibase.nodes.node_logger.protocols.protocol_logger_emit_log_event import ProtocolLoggerEmitLogEvent

class ToolLoggerEmitLogEvent(ProtocolLoggerEmitLogEvent):
    """
    Canonical tool implementation for structured log event emission in ONEX logger node.
    Implements ProtocolLoggerEmitLogEvent.
    All helpers (decorators, context managers) are now instance methods for DI/testability.
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
        context = self._create_log_context_from_frame()
        node_id = node_id or context.node_id
        correlation_id = correlation_id or self._get_or_generate_correlation_id()
        self._route_to_logger_node(
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
        self,
        level: LogLevelEnum,
        message: str,
        event_type: str = "generic",
        node_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        event_bus: Optional[ProtocolEventBus] = None,
    ) -> None:
        self.emit_log_event(
            level=level,
            event_type=event_type,
            message=message,
            node_id=node_id,
            correlation_id=correlation_id,
            data=data,
            event_bus=event_bus,
        )

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
        self.emit_log_event(
            level=level,
            event_type=event_type,
            message=message,
            node_id=node_id,
            correlation_id=correlation_id,
            data=data,
            event_bus=event_bus,
        )

    def trace_function_lifecycle(self, func: Callable) -> Callable:
        """
        Decorator to automatically log function entry/exit with TRACE level.
        """
        def wrapper(*args, **kwargs):
            correlation_id = self._get_or_generate_correlation_id()
            context = self._create_log_context_from_frame()
            self.emit_log_event(
                level=LogLevelEnum.TRACE,
                event_type="function_entry",
                message=f"Entering {func.__name__}",
                correlation_id=correlation_id,
                data={"function": func.__name__},
            )
            try:
                result = func(*args, **kwargs)
                self.emit_log_event(
                    level=LogLevelEnum.TRACE,
                    event_type="function_exit",
                    message=f"Exiting {func.__name__}",
                    correlation_id=correlation_id,
                    data={"function": func.__name__, "success": True},
                )
                return result
            except Exception as e:
                self.emit_log_event(
                    level=LogLevelEnum.ERROR,
                    event_type="function_exception",
                    message=f"Exception in {func.__name__}: {str(e)}",
                    correlation_id=correlation_id,
                    data={"function": func.__name__, "success": False, "exception_type": type(e).__name__, "exception_message": str(e)},
                )
                raise
        return wrapper

    def tool_logger_performance_metrics(self, threshold_ms: int = 1000) -> Callable:
        """
        Decorator to log performance metrics for functions.
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                function_name = func.__name__
                correlation_id = self._get_or_generate_correlation_id()
                start_time = datetime.utcnow()
                result = func(*args, **kwargs)
                end_time = datetime.utcnow()
                execution_time_ms = (end_time - start_time).total_seconds() * 1000
                if execution_time_ms > threshold_ms:
                    self.emit_log_event(
                        level=LogLevelEnum.WARNING,
                        event_type="performance_threshold_exceeded",
                        message=f"Function {function_name} exceeded performance threshold",
                        correlation_id=correlation_id,
                        data={
                            "function": function_name,
                            "execution_time_ms": execution_time_ms,
                            "threshold_ms": threshold_ms,
                            "operation_name": function_name,
                        },
                    )
                else:
                    self.emit_log_event(
                        level=LogLevelEnum.DEBUG,
                        event_type="performance_metrics",
                        message=f"Function {function_name} performance metrics",
                        correlation_id=correlation_id,
                        data={
                            "function": function_name,
                            "execution_time_ms": execution_time_ms,
                            "threshold_ms": threshold_ms,
                            "operation_name": function_name,
                        },
                    )
                return result
            return wrapper
        return decorator

    class ToolLoggerCodeBlock:
        """
        Context manager for logging code block entry/exit and exceptions.
        Now takes a reference to the parent ToolLoggerEmitLogEvent instance for DI/mocking.
        """
        def __init__(
            self,
            parent: 'ToolLoggerEmitLogEvent',
            block_name: str,
            correlation_id: Optional[str] = None,
            level: LogLevelEnum = LogLevelEnum.DEBUG,
            data: Optional[Dict[str, Any]] = None,
        ):
            self.parent = parent
            self.block_name = block_name
            self.correlation_id = correlation_id or parent._get_or_generate_correlation_id()
            self.level = level
            self.data = data or {}

        def __enter__(self):
            self.parent.emit_log_event(
                level=self.level,
                event_type="code_block_entry",
                message=f"Entering code block {self.block_name}",
                correlation_id=self.correlation_id,
                data={"block_name": self.block_name, **self.data},
            )
            self.start_time = datetime.utcnow()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            end_time = datetime.utcnow()
            execution_time_ms = (end_time - self.start_time).total_seconds() * 1000
            if exc_type is None:
                self.parent.emit_log_event(
                    level=self.level,
                    event_type="code_block_exit",
                    message=f"Exiting code block {self.block_name}",
                    correlation_id=self.correlation_id,
                    data={
                        "block_name": self.block_name,
                        "execution_time_ms": execution_time_ms,
                        "success": True,
                        **self.data,
                    },
                )
            else:
                self.parent.emit_log_event(
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
                    },
                )

    @staticmethod
    def _get_or_generate_correlation_id() -> str:
        correlation_id = os.getenv("ONEX_CORRELATION_ID")
        if correlation_id:
            return correlation_id
        return str(uuid.uuid4())[:8]

    @staticmethod
    def _detect_node_id_from_context() -> str:
        frame = inspect.currentframe()
        try:
            while frame:
                frame = frame.f_back
                if frame and 'self' in frame.f_locals:
                    obj = frame.f_locals['self']
                    if hasattr(obj, 'node_id'):
                        return obj.node_id
                    elif hasattr(obj, '__class__') and 'node' in obj.__class__.__name__.lower():
                        return obj.__class__.__name__
            caller_frame = inspect.currentframe().f_back.f_back
            if caller_frame:
                module_name = caller_frame.f_globals.get('__name__', 'unknown')
                return module_name.split('.')[-1]
            return "unknown"
        finally:
            del frame

    @staticmethod
    def _create_log_context_from_frame() -> LogContextModel:
        frame = inspect.currentframe().f_back.f_back
        if frame:
            return LogContextModel(
                calling_function=frame.f_code.co_name,
                calling_module=frame.f_globals.get('__name__', 'unknown'),
                calling_line=frame.f_lineno,
                timestamp=datetime.utcnow().isoformat(),
                node_id=ToolLoggerEmitLogEvent._detect_node_id_from_context(),
                correlation_id=None,
            )
        else:
            return LogContextModel(
                calling_function="unknown",
                calling_module="unknown", 
                calling_line=0,
                timestamp=datetime.utcnow().isoformat(),
                node_id="unknown",
                correlation_id=None,
            )

    @staticmethod
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
        try:
            config = create_default_config()
            formatter = create_smart_formatter(config)
            output_handler = ToolContextAwareOutputHandler(config)
            formatted_log = formatter.format_log_event(
                level=level,
                event_type=event_type,
                message=message,
                context=context,
                data=data,
                correlation_id=correlation_id,
            )
            output_handler.output_log_entry(formatted_log, level.name)
        except Exception as e:
            fallback_message = f"[{level.name}] {message} [{correlation_id}] (logger routing failed: {str(e)})"
            print(fallback_message)

# TODO: Refactor to remove any remaining direct core/runtime imports except protocols.
# TODO: Ensure all dependencies are registry-injected in production usage. 