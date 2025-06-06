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
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import ModelEventBusConfig
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import (
    emit_log_event_sync,
    make_log_context,
)

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
            make_log_context(node_id="node_kafka_event_bus"),
        )

    async def connect(self):
        """Async: Establish connection to Kafka cluster. If no broker is available, degrade gracefully and delegate to InMemoryEventBus."""
        import os

        from aiokafka.errors import KafkaConnectionError

        try:
            producer_kwargs = {
                "bootstrap_servers": self.bootstrap_servers,
                "client_id": self.config.client_id,
                "acks": self.config.acks,
            }
            consumer_kwargs = {
                "bootstrap_servers": self.bootstrap_servers,
                "group_id": self.group_id,
                "enable_auto_commit": self.config.enable_auto_commit,
                "auto_offset_reset": self.config.auto_offset_reset,
                "client_id": self.config.client_id,
            }
            # SASL/TLS config
            if self.config.security_protocol:
                producer_kwargs["security_protocol"] = self.config.security_protocol
                consumer_kwargs["security_protocol"] = self.config.security_protocol
            if self.config.sasl_mechanism:
                producer_kwargs["sasl_mechanism"] = self.config.sasl_mechanism
                consumer_kwargs["sasl_mechanism"] = self.config.sasl_mechanism
            # Secrets injection: prefer env vars if config is not set
            sasl_username = self.config.sasl_username or os.environ.get(
                "KAFKA_SASL_USERNAME"
            )
            sasl_password = self.config.sasl_password or os.environ.get(
                "KAFKA_SASL_PASSWORD"
            )
            if sasl_username:
                producer_kwargs["sasl_plain_username"] = sasl_username
                consumer_kwargs["sasl_plain_username"] = sasl_username
            if sasl_password:
                producer_kwargs["sasl_plain_password"] = sasl_password
                consumer_kwargs["sasl_plain_password"] = sasl_password
            # TLS config
            if self.config.ssl_cafile:
                producer_kwargs["ssl_cafile"] = self.config.ssl_cafile
                consumer_kwargs["ssl_cafile"] = self.config.ssl_cafile
            if self.config.ssl_certfile:
                producer_kwargs["ssl_certfile"] = self.config.ssl_certfile
                consumer_kwargs["ssl_certfile"] = self.config.ssl_certfile
            if self.config.ssl_keyfile:
                producer_kwargs["ssl_keyfile"] = self.config.ssl_keyfile
                consumer_kwargs["ssl_keyfile"] = self.config.ssl_keyfile
            # Document: All sensitive fields can be injected via env vars for CI/secrets management
            self.producer = AIOKafkaProducer(**producer_kwargs)
            await self.producer.start()
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                **consumer_kwargs,
            )
            await self.consumer.start()
            self.logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
            self.connected = True
        except KafkaConnectionError as e:
            self.logger.warning(
                f"Kafka broker not available: {e}. Running in degraded mode (no broker). Delegating to InMemoryEventBus."
            )
            self.connected = False
            self.fallback_bus = InMemoryEventBus()
        except KafkaError as e:
            self.logger.error(f"Kafka connection failed: {e}")
            self.connected = False
            self.fallback_bus = InMemoryEventBus()
            raise

    async def publish(self, message: bytes, key: Optional[bytes] = None):
        """
        Async: Publish a message to the Kafka topic. Delegate to fallback bus in degraded mode.
        - Uses correlation_id (if present) or node_id as the Kafka message key for partitioning.
        """
        if not self.connected:
            if self.fallback_bus:
                return await self.fallback_bus.publish(message)
            self.logger.warning(
                "KafkaEventBus in degraded mode: publish() is a no-op (no broker connected). Message not sent."
            )
            return
        if not self.producer:
            raise RuntimeError("Producer not connected. Call connect() first.")
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
            self.logger.error(f"Kafka publish failed: {e}")
            raise

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
            raise RuntimeError("Consumer not connected. Call connect() with group_id.")
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[KafkaEventBus] Starting async subscribe loop for topics: {self.topics}, group_id: {self.group_id}",
            make_log_context(node_id="node_kafka_event_bus"),
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
                    make_log_context(node_id="node_kafka_event_bus"),
                )

    async def close(self):
        if not self.connected and self.fallback_bus:
            return await self.fallback_bus.close()
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
        self.logger.info("Kafka connections closed.")

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


# TODO: Add partitioning, ack, error handling, and advanced features as per checklist.
