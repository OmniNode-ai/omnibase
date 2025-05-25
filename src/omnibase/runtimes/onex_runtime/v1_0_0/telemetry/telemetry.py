# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: telemetry.py
# version: 1.0.0
# uuid: cbebb449-a1ef-4147-9ef7-ee2b8f920b28
# author: OmniNode Team
# created_at: 2025-05-25T13:27:02.838110
# last_modified_at: 2025-05-25T17:35:42.321323
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 1460a2addf01a3eba8f9eadae37602d57db87acd306b6a07d5e366548f47b9a8
# entrypoint: python@telemetry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.telemetry
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Telemetry decorator for ONEX node entrypoints.

This module provides a decorator that standardizes logging context, timing,
event emission, and error handling for all node entrypoints.
"""

import functools
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar

from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.model.model_onex_message_result import OnexResultModel

F = TypeVar("F", bound=Callable[..., Any])

# Global event bus for telemetry subscribers
_telemetry_event_handlers: List[Callable[[OnexEvent], None]] = []


def register_telemetry_handler(handler: Callable[[OnexEvent], None]) -> None:
    """
    Register a handler for telemetry events.

    Args:
        handler: Function that will be called with each telemetry event
    """
    _telemetry_event_handlers.append(handler)


def unregister_telemetry_handler(handler: Callable[[OnexEvent], None]) -> None:
    """
    Unregister a telemetry event handler.

    Args:
        handler: Handler function to remove
    """
    if handler in _telemetry_event_handlers:
        _telemetry_event_handlers.remove(handler)


def clear_telemetry_handlers() -> None:
    """Clear all registered telemetry handlers."""
    _telemetry_event_handlers.clear()


def telemetry(
    node_name: str,
    operation: str,
    emit_events: bool = True,
    log_context: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """
    Telemetry decorator for node entrypoints.

    This decorator provides:
    - Standardized logging context with correlation IDs
    - Execution timing and performance metrics
    - Event emission for observability
    - Consistent error handling and reporting

    Args:
        node_name: Name of the node (e.g., "stamper_node")
        operation: Name of the operation (e.g., "process_file", "process_directory")
        emit_events: Whether to emit telemetry events
        log_context: Additional context to include in logs

    Returns:
        Decorated function with telemetry capabilities
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate correlation ID if not provided
            correlation_id = kwargs.get("correlation_id") or str(uuid.uuid4())
            kwargs["correlation_id"] = correlation_id

            # Start timing
            start_time = time.time()

            # Emit start event
            if emit_events:
                start_event = OnexEvent(
                    event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
                    correlation_id=correlation_id,
                    node_id=node_name,
                    timestamp=datetime.fromtimestamp(start_time),
                    metadata={
                        "operation": operation,
                        "function": func.__name__,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                    },
                )
                _emit_event(start_event)

            try:
                # Execute the function
                result = func(*args, **kwargs)

                # Calculate execution time
                execution_time = time.time() - start_time

                # Emit success event
                if emit_events:
                    success_event = OnexEvent(
                        event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
                        correlation_id=correlation_id,
                        node_id=node_name,
                        timestamp=datetime.utcnow(),
                        metadata={
                            "operation": operation,
                            "function": func.__name__,
                            "execution_time_ms": round(execution_time * 1000, 2),
                            "result_type": type(result).__name__,
                            "success": True,
                        },
                    )
                    _emit_event(success_event)

                # Add telemetry metadata to result if it's an OnexResultModel
                if isinstance(result, OnexResultModel):
                    result.metadata = result.metadata or {}
                    result.metadata.update(
                        {
                            "telemetry": {
                                "correlation_id": correlation_id,
                                "execution_time_ms": round(execution_time * 1000, 2),
                                "node_name": node_name,
                                "operation": operation,
                            }
                        }
                    )

                return result

            except Exception as e:
                # Calculate execution time for error case
                execution_time = time.time() - start_time

                # Emit error event
                if emit_events:
                    error_event = OnexEvent(
                        event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR,
                        correlation_id=correlation_id,
                        node_id=node_name,
                        timestamp=datetime.utcnow(),
                        metadata={
                            "operation": operation,
                            "function": func.__name__,
                            "execution_time_ms": round(execution_time * 1000, 2),
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                            "success": False,
                        },
                    )
                    _emit_event(error_event)

                # Re-raise the exception
                raise

        return wrapper  # type: ignore

    return decorator


def _emit_event(event: OnexEvent) -> None:
    """
    Emit a telemetry event.

    This function emits events to both the logging system (for backward compatibility)
    and to any registered event handlers (for real-time monitoring).

    Args:
        event: The event to emit
    """
    # Emit to logging system (existing behavior)
    logger = logging.getLogger(f"telemetry.{event.node_id}")
    operation = (
        event.metadata.get("operation", "unknown") if event.metadata else "unknown"
    )
    logger.info(
        f"[{event.event_type}] {operation} - {event.correlation_id}",
        extra={
            "event_type": event.event_type,
            "correlation_id": event.correlation_id,
            "node_id": event.node_id,
            "operation": operation,
            "timestamp": event.timestamp,
            "metadata": event.metadata,
        },
    )

    # Emit to registered event handlers
    for handler in _telemetry_event_handlers:
        try:
            handler(event)
        except Exception as e:
            # Don't let handler errors break the main application
            logger.warning(f"Telemetry handler error: {e}")


def get_correlation_id_from_state(state: Any) -> Optional[str]:
    """
    Extract correlation ID from input state if available.

    Args:
        state: Input state object that may contain a correlation_id

    Returns:
        Correlation ID if found, None otherwise
    """
    if hasattr(state, "correlation_id"):
        correlation_id = getattr(state, "correlation_id")
        return str(correlation_id) if correlation_id is not None else None
    if hasattr(state, "metadata") and state.metadata:
        correlation_id = state.metadata.get("correlation_id")
        return str(correlation_id) if correlation_id is not None else None
    return None


def add_correlation_id_to_state(state: Any, correlation_id: str) -> None:
    """
    Add correlation ID to state object if possible.

    Args:
        state: State object to modify
        correlation_id: Correlation ID to add
    """
    if hasattr(state, "correlation_id"):
        state.correlation_id = correlation_id
    elif hasattr(state, "metadata"):
        if state.metadata is None:
            state.metadata = {}
        state.metadata["correlation_id"] = correlation_id
