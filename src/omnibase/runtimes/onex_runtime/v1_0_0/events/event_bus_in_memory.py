# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.336901'
# description: Stamped by PythonHandler
# entrypoint: python://event_bus_in_memory
# hash: 7e0863fd4dc8770deae28d74166370ef8631a63c3f81660f17dd75fe916f7840
# last_modified_at: '2025-05-29T14:14:00.410845+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: event_bus_in_memory.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: c0ff478c-011b-4afe-9595-ff748e5ede75
# version: 1.0.0
# === /OmniNode:Metadata ===

import datetime
import threading
import time
import uuid
from typing import Callable, Optional, Set, Tuple

from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums.log_level import LogLevelEnum
from omnibase.model.model_log_entry import LogContextModel
from omnibase.model.model_onex_event import OnexEvent
from omnibase.protocol.protocol_event_bus_types import (
    EventBusCredentialsModel,
    ProtocolEventBus,
)


class InMemoryEventBus(ProtocolEventBus):
    """
    Canonical in-memory implementation of ProtocolEventBus for ONEX.
    Supports synchronous publish/subscribe for local event emission and testing.
    Now exposes basic metrics and health checks for observability.
    """

    def __init__(self, credentials: Optional[EventBusCredentialsModel] = None) -> None:
        self.credentials = credentials
        self._bus_id = str(uuid.uuid4())
        self._subscribers: Set[Callable[[OnexEvent], None]] = set()
        self._event_count = 0
        self._error_count = 0
        self._last_event_ts = None
        self._lock = threading.Lock()
        self._on_error: Optional[Callable[[Exception, OnexEvent], None]] = None

    @property
    def bus_id(self) -> str:
        return self._bus_id

    @property
    def event_count(self):
        """Total number of events successfully dispatched."""
        return self._event_count

    @property
    def error_count(self):
        """Total number of errors encountered during event dispatch."""
        return self._error_count

    @property
    def last_event_timestamp(self):
        """Timestamp of the last successfully received event."""
        return self._last_event_ts

    def health_check(self) -> dict:
        """
        Returns a health summary of the event bus (metrics, subscriber count).
        """
        return {
            "event_count": self._event_count,
            "error_count": self._error_count,
            "last_event_ts": self._last_event_ts,
            "subscriber_count": len(self._subscribers),
        }

    def publish(self, event: OnexEvent) -> None:
        for callback in list(self._subscribers):
            try:
                callback(event)
            except Exception as exc:
                self._error_count += 1
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"[InMemoryEventBus] Subscriber {id(callback)} raised exception: {exc}",
                    event_bus=self,
                )
                if self._on_error:
                    try:
                        self._on_error(exc, event)
                    except Exception as handler_exc:
                        emit_log_event_sync(
                            LogLevelEnum.ERROR,
                            f"[InMemoryEventBus] Error handler raised exception: {handler_exc}",
                            event_bus=self,
                        )
        # Note: No logging here to avoid circular dependencies during structured logging setup
        with self._lock:
            self._event_count += 1
            self._last_event_ts = time.time()

    def subscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[InMemoryEventBus] subscribe called: callback_id={id(callback)}, total_subscribers={len(self._subscribers)}",
            event_bus=self,
        )
        # Note: No logging here to avoid circular dependencies during structured logging setup
        with self._lock:
            self._subscribers.add(callback)

    def unsubscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            "InMemoryEventBus unsubscribe called",
            context=LogContextModel(
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                calling_module=__name__,
                calling_function="unsubscribe",
                calling_line=__import__("inspect").currentframe().f_lineno,
                event_bus_type="inmemory",
                operation="unsubscribe",
                subscriber_id=id(callback),
                credentials_present=self.credentials is not None,
            ),
            event_bus=self,
        )
        # Note: No logging here to avoid circular dependencies during structured logging setup
        with self._lock:
            self._subscribers.discard(callback)

    def clear(self) -> None:
        emit_log_event_sync(
            LogLevelEnum.INFO,
            "InMemoryEventBus clear called",
            context=LogContextModel(
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                calling_module=__name__,
                calling_function="clear",
                calling_line=__import__("inspect").currentframe().f_lineno,
                event_bus_type="inmemory",
                operation="clear",
                credentials_present=self.credentials is not None,
            ),
            event_bus=self,
        )
        # Note: No logging here to avoid circular dependencies during structured logging setup
        with self._lock:
            self._subscribers.clear()

    def set_error_handler(
        self, handler: Callable[[Exception, OnexEvent], None]
    ) -> None:
        emit_log_event_sync(
            LogLevelEnum.INFO,
            "InMemoryEventBus set_error_handler called",
            context=LogContextModel(
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                calling_module=__name__,
                calling_function="set_error_handler",
                calling_line=__import__("inspect").currentframe().f_lineno,
                event_bus_type="inmemory",
                operation="set_error_handler",
                handler_id=id(handler),
                credentials_present=self.credentials is not None,
            ),
            event_bus=self,
        )
        self._on_error = handler

    async def publish_async(self, event: OnexEvent) -> None:
        # For in-memory, just call sync publish (fast, no IO)
        self.publish(event)

    async def subscribe_async(self, callback: Callable[[OnexEvent], None]) -> None:
        self.subscribe(callback)

    async def unsubscribe_async(self, callback: Callable[[OnexEvent], None]) -> None:
        self.unsubscribe(callback)

    # TODO: For high-throughput or async scenarios, replace synchronous dispatch with asyncio.Queue or async event loop for subscriber dispatch.
