# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.702836'
# description: Stamped by PythonHandler
# entrypoint: python://telemetry
# hash: 9dfdc783ef187ffd707a08bb0de6de51f29430460a52a450c0525713bbfb3448
# last_modified_at: '2025-05-29T14:14:00.899155+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: telemetry.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.telemetry.telemetry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 8d2e2616-9592-4175-a957-fba2bb86caac
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Telemetry decorator for ONEX node entrypoints.

This module provides a decorator that standardizes logging context, timing,
event emission, and error handling for all node entrypoints.
"""

import functools
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar

from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum
from omnibase.model.model_onex_event import (
    OnexEvent,
    OnexEventTypeEnum,
    TelemetryOperationErrorMetadataModel,
    TelemetryOperationStartMetadataModel,
    TelemetryOperationSuccessMetadataModel,
)
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_event_bus import ProtocolEventBus

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem

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
    event_bus: Optional[ProtocolEventBus] = None,
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
        event_bus: Optional event bus for event emission. If not provided, uses global handlers.

    Returns:
        Decorated function with telemetry capabilities
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract event_bus from kwargs if provided at runtime
            runtime_event_bus = kwargs.get("event_bus", None) or event_bus
            emit_log_event_sync(
                LogLevelEnum.DEBUG,
                f"[telemetry] wrapper: runtime_event_bus id={id(runtime_event_bus)}",
                node_id=_COMPONENT_NAME,
                event_bus=runtime_event_bus,
            )
            if runtime_event_bus is None:
                raise RuntimeError(
                    "telemetry decorator requires an explicit event_bus argument (protocol purity)"
                )

            # Generate correlation ID if not provided
            correlation_id = kwargs.get("correlation_id") or str(uuid.uuid4())
            kwargs["correlation_id"] = correlation_id

            # Start timing
            start_time = time.time()

            # Emit start event
            if emit_events:
                start_metadata = TelemetryOperationStartMetadataModel(
                    operation=operation,
                    function=func.__name__,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                )
                start_event = OnexEvent(
                    event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
                    correlation_id=correlation_id,
                    node_id=node_name,
                    timestamp=datetime.fromtimestamp(start_time),
                    metadata=start_metadata,
                )
                emit_log_event_sync(
                    LogLevelEnum.DEBUG,
                    f"[telemetry] Creating TELEMETRY_OPERATION_START event: correlation_id={correlation_id}",
                    node_id=_COMPONENT_NAME,
                    event_bus=runtime_event_bus,
                )
                _emit_event(start_event, runtime_event_bus)

            try:
                # Execute the function
                result = func(*args, **kwargs)

                # Calculate execution time
                execution_time = time.time() - start_time

                # Emit success event
                if emit_events:
                    success_metadata = TelemetryOperationSuccessMetadataModel(
                        operation=operation,
                        function=func.__name__,
                        execution_time_ms=round(execution_time * 1000, 2),
                        result_type=type(result).__name__,
                        success=True,
                    )
                    success_event = OnexEvent(
                        event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
                        correlation_id=correlation_id,
                        node_id=node_name,
                        timestamp=datetime.utcnow(),
                        metadata=success_metadata,
                    )
                    emit_log_event_sync(
                        LogLevelEnum.DEBUG,
                        f"[telemetry] Creating TELEMETRY_OPERATION_SUCCESS event: correlation_id={correlation_id}",
                        node_id=_COMPONENT_NAME,
                        event_bus=runtime_event_bus,
                    )
                    _emit_event(success_event, runtime_event_bus)

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
                    error_metadata = TelemetryOperationErrorMetadataModel(
                        operation=operation,
                        function=func.__name__,
                        execution_time_ms=round(execution_time * 1000, 2),
                        error_type=type(e).__name__,
                        error_message=str(e),
                        success=False,
                    )
                    error_event = OnexEvent(
                        event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR,
                        correlation_id=correlation_id,
                        node_id=node_name,
                        timestamp=datetime.utcnow(),
                        metadata=error_metadata,
                    )
                    emit_log_event_sync(
                        LogLevelEnum.DEBUG,
                        f"[telemetry] Creating TELEMETRY_OPERATION_ERROR event: correlation_id={correlation_id}",
                        node_id=_COMPONENT_NAME,
                        event_bus=runtime_event_bus,
                    )
                    _emit_event(error_event, runtime_event_bus)

                # Re-raise the exception
                raise

        return wrapper  # type: ignore

    return decorator


def _emit_event(event: OnexEvent, event_bus: Optional[ProtocolEventBus] = None) -> None:
    """
    Emit a telemetry event.

    Args:
        event: The event to emit
        event_bus: Event bus to use. Must not be None (protocol purity).
    """
    if event_bus is None:
        raise RuntimeError(
            "_emit_event requires an explicit event_bus argument (protocol purity)"
        )
    try:
        # Validate event schema before emission
        from omnibase.runtimes.onex_runtime.v1_0_0.telemetry.event_schema_validator import (
            validate_event_schema,
        )

        # Use non-strict validation for backward compatibility
        validate_event_schema(event, strict_mode=False, event_bus=event_bus)

        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[telemetry] _emit_event: event_bus id={id(event_bus)}, event_type={event.event_type}",
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )
        # Emit to event bus
        event_bus.publish(event)

        # Also emit to global handlers for backward compatibility
        for handler in _telemetry_event_handlers:
            try:
                handler(event)
            except Exception as e:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"Error in telemetry handler: {e}",
                    node_id=_COMPONENT_NAME,
                    event_bus=event_bus,
                )

    except Exception as e:
        # Log validation or emission errors but don't fail the operation
        emit_log_event_sync(
            LogLevelEnum.WARNING,
            f"Error emitting telemetry event: {e}",
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )


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
