"""
Kafka Event Bus – Event Replay Policy

- On reconnection or restart, the Kafka consumer resumes from the last committed offset (using Kafka's consumer group mechanism).
- If the offset is lost or reset, consumption starts from the configured offset reset policy (typically 'earliest' for replay, or 'latest' for only new events).
- Events are retained in Kafka topics for a configurable period (e.g., 7 days) to allow for replay.
- Event handlers must be idempotent to avoid side effects from replayed events.
- In degraded (in-memory) mode, replay is not possible; only live events are processed.
- The node logs when a replay occurs and how many events are replayed (future enhancement: add explicit replay metrics/logs).

Event Keying and Partitioning Strategy:
- Kafka messages are keyed by correlation_id (if present), else node_id, else a default.
- This ensures all events for a given correlation or node are routed to the same partition, preserving order.
- For dev/CI, a single partition is sufficient; for production, use multiple partitions for scalability.
"""

import asyncio
import json
import logging
import random
import string
import typing
from typing import Any, Callable, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError
from kafka.admin import KafkaAdminClient
from pydantic import BaseModel

from omnibase.enums.log_level import LogLevelEnum
from omnibase.model.model_onex_event import OnexEvent
from omnibase.model.model_event_bus_config import ModelEventBusConfig
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context
from omnibase.nodes.node_kafka_event_bus.constants import NODE_KAFKA_EVENT_BUS_ID
from ..error_codes import NodeKafkaEventBusNodeErrorCode
from omnibase.core.core_errors import OnexError

if typing.TYPE_CHECKING:
    from omnibase.protocol.protocol_event_bus import ProtocolEventBus


class KafkaHealthCheckResult(BaseModel):
    connected: bool
    error: str = None


class KafkaEventBus:
    """
    Canonical Async Kafka Event Bus implementation for ONEX.
    Implements ProtocolEventBus and emits OnexEvent objects.
    Uses ModelEventBusConfig for all configuration.
    Only async methods are supported; sync methods are not implemented.
    """

    def __init__(self, config: ModelEventBusConfig):
        self.config = config
        self.producer = None
        self.consumer = None
        self.logger = logging.getLogger("KafkaEventBus")
        self.bootstrap_servers = config.bootstrap_servers
        self.topics = config.topics
        rand_suffix = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )
        self.group_id = f"{config.group_id}-{rand_suffix}"
        self.connected = False
        self.fallback_bus = None  # InMemoryEventBus for degraded mode
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[KafkaEventBus] (async) Producer/consumer instantiated for this instance only (id={id(self)})",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
        )
        emit_log_event_sync(
            LogLevelEnum.INFO,
            "[KafkaEventBus] Only async methods are available (publish_async, subscribe_async, etc.)",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
        )

    async def connect(self):
        from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
        emit_log_event_sync(LogLevelEnum.DEBUG, f"[KafkaEventBus] connect() called", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
        try:
            from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
            loop = asyncio.get_event_loop()
            self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers, loop=loop)
            await self.producer.start()
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                loop=loop
            )
            await self.consumer.start()
            self.connected = True
            emit_log_event_sync(LogLevelEnum.INFO, f"[KafkaEventBus] Connected to Kafka at {self.bootstrap_servers}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
        except Exception as e:
            emit_log_event_sync(LogLevelEnum.ERROR, f"[KafkaEventBus] connect() failed: {e}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
            self.connected = False

    async def publish(self, message: bytes, key: Optional[bytes] = None):
        """
        Async: Publish a message to the Kafka topic. Delegate to fallback bus in degraded mode.
        - Uses correlation_id (if present) or node_id as the Kafka message key for partitioning.
        """
        if not self.connected:
            if self.fallback_bus:
                return await self.fallback_bus.publish(message)
            self.logger.warning(
                f"KafkaEventBus in degraded mode: publish() is a no-op (no broker connected). Message not sent. [ErrorCode: {NodeKafkaEventBusNodeErrorCode.BACKEND_UNAVAILABLE.value}]"
            )
            return
        if not self.producer:
            raise OnexError(NodeKafkaEventBusNodeErrorCode.BACKEND_UNAVAILABLE, "Kafka producer not connected. Call connect() first.")
        try:
            # Extract key from message if not provided
            if key is None:
                try:
                    event = json.loads(message)
                    key_val = (
                        event.get("correlation_id") or event.get("node_id") or "default"
                    )
                    key = str(key_val).encode()
                except Exception:
                    key = b"default"
            await self.producer.send_and_wait(self.topics[0], message, key=key)
            self.logger.info(f"Published message to {self.topics}")
        except KafkaError as e:
            self.logger.error(f"Kafka publish failed: {e} [ErrorCode: {NodeKafkaEventBusNodeErrorCode.MESSAGE_PUBLISH_FAILED.value}]")
            raise OnexError(NodeKafkaEventBusNodeErrorCode.MESSAGE_PUBLISH_FAILED, "Failed to publish message to Kafka.")

    async def subscribe(self, on_message: Callable[[Any], None]):
        """Async: Subscribe to the Kafka topic and process messages with the given callback. Delegate to fallback bus in degraded mode."""
        if not self.connected:
            if self.fallback_bus:
                return await self.fallback_bus.subscribe(on_message)
            self.logger.warning(
                "KafkaEventBus in degraded mode: subscribe() is a no-op (no broker connected)."
            )
            return
        if not self.consumer:
            raise OnexError(NodeKafkaEventBusNodeErrorCode.BACKEND_UNAVAILABLE, "Kafka consumer not connected. Call connect() with group_id.")
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[KafkaEventBus] Starting async subscribe loop for topics: {self.topics}, group_id: {self.group_id}",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
        )
        async for msg in self.consumer:
            try:
                event = OnexEvent.parse_raw(msg.value)
                if asyncio.iscoroutinefunction(on_message):
                    await on_message(event)
                else:
                    on_message(event)
            except Exception as cb_exc:
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"[KafkaEventBus] Exception in event handler callback: {cb_exc}",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
                )

    async def close(self):
        if not self.connected and self.fallback_bus:
            return await self.fallback_bus.close()
        if self.producer:
            await self.producer.stop()
            self.producer = None
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None
        self.logger.info("Kafka connections closed.")
        emit_log_event_sync(LogLevelEnum.DEBUG, "KafkaEventBus closed", make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))

    async def health_check(self) -> KafkaHealthCheckResult:
        """Async health check: try to connect to Kafka broker and return status."""
        from aiokafka.errors import KafkaConnectionError

        try:
            producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
            await producer.start()
            await producer.stop()
            return KafkaHealthCheckResult(connected=True)
        except KafkaConnectionError as e:
            return KafkaHealthCheckResult(connected=False, error=str(e))
        except Exception as e:
            return KafkaHealthCheckResult(connected=False, error=str(e))

    # --- Protocol-compliant async methods ---
    async def publish_async(self, event: OnexEvent) -> None:
        # Serialize event to bytes and publish
        message = event.model_dump_json().encode()
        if not self.connected:
            emit_log_event_sync(LogLevelEnum.WARNING, f"[KafkaEventBus] publish_async: not connected, fallback or no-op", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
            if self.fallback_bus:
                await self.fallback_bus.publish_async(event)
            else:
                self.logger.warning("KafkaEventBus in degraded mode: publish_async() is a no-op (no broker connected). Message not sent.")
            return
        if not self.producer:
            emit_log_event_sync(LogLevelEnum.ERROR, f"[KafkaEventBus] publish_async: producer not connected", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
            raise OnexError(NodeKafkaEventBusNodeErrorCode.BACKEND_UNAVAILABLE, "Kafka producer not connected. Call connect() first.")
        try:
            # Extract key from event
            key_val = getattr(event, "correlation_id", None) or getattr(event, "node_id", None) or "default"
            key = str(key_val).encode()
            await self.producer.send_and_wait(self.topics[0], message, key=key)
            emit_log_event_sync(LogLevelEnum.INFO, f"[KafkaEventBus] Published message to {self.topics}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
        except KafkaError as e:
            emit_log_event_sync(LogLevelEnum.ERROR, f"[KafkaEventBus] Kafka publish failed: {e}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
            self.logger.error(f"Kafka publish failed: {e}")
            raise

    async def subscribe_async(self, callback: Callable[[OnexEvent], None]) -> None:
        from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
        emit_log_event_sync(LogLevelEnum.DEBUG, f"[KafkaEventBus] subscribe_async called. Connected: {self.connected}, Consumer: {self.consumer}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
        if not self.connected:
            emit_log_event_sync(LogLevelEnum.WARNING, f"[KafkaEventBus] subscribe_async: not connected, fallback or no-op", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
            if self.fallback_bus:
                await self.fallback_bus.subscribe_async(callback)
            else:
                self.logger.warning("KafkaEventBus in degraded mode: subscribe_async() is a no-op (no broker connected).")
            return
        if not self.consumer:
            emit_log_event_sync(LogLevelEnum.ERROR, f"[KafkaEventBus] subscribe_async: consumer not connected", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
            raise OnexError(NodeKafkaEventBusNodeErrorCode.BACKEND_UNAVAILABLE, "Kafka consumer not connected. Call connect() with group_id.")
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[KafkaEventBus] Starting async subscribe loop for topics: {self.topics}, group_id: {self.group_id}",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
        )
        async for msg in self.consumer:
            try:
                emit_log_event_sync(LogLevelEnum.DEBUG, f"[KafkaEventBus] Received message: {msg}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
                event = OnexEvent.parse_raw(msg.value)
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as cb_exc:
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"[KafkaEventBus] Exception in event handler callback: {cb_exc}",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
                )

    async def unsubscribe_async(self, callback: Callable[[OnexEvent], None]) -> None:
        # Not implemented for Kafka (would require consumer group management)
        raise OnexError(NodeKafkaEventBusNodeErrorCode.UNSUPPORTED_OPERATION, "unsubscribe_async is not implemented for KafkaEventBus.")

    @property
    def bus_id(self) -> str:
        return f"kafka:{self.bootstrap_servers}:{self.group_id}"


# TODO: Add partitioning, ack, error handling, and advanced features as per checklist.
