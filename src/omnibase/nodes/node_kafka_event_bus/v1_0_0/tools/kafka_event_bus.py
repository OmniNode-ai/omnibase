from typing import Optional, Callable, Any
import logging
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import KafkaEventBusConfigModel
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError
from omnibase.model.model_onex_event import OnexEvent
import typing
import asyncio
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from kafka.admin import KafkaAdminClient
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
import json
import random
import string
from pydantic import BaseModel
if typing.TYPE_CHECKING:
    from omnibase.protocol.protocol_event_bus import ProtocolEventBus

class KafkaHealthCheckResult(BaseModel):
    connected: bool
    error: str = None

class KafkaEventBus:
    """
    Canonical Async Kafka Event Bus implementation for ONEX.
    Implements ProtocolEventBus and emits OnexEvent objects.
    Uses KafkaEventBusConfigModel for all configuration.
    """
    def __init__(self, config: KafkaEventBusConfigModel):
        self.config = config
        self.producer = None
        self.consumer = None
        self.logger = logging.getLogger("KafkaEventBus")
        self.bootstrap_servers = config.bootstrap_servers
        self.topics = config.topics
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        self.group_id = f"{config.group_id}-{rand_suffix}"
        self.connected = False
        self.fallback_bus = None  # InMemoryEventBus for degraded mode
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[KafkaEventBus] (async) Producer/consumer instantiated for this instance only (id={id(self)})",
            make_log_context(node_id="node_kafka_event_bus")
        )

    async def connect(self):
        """Async: Establish connection to Kafka cluster. If no broker is available, degrade gracefully and delegate to InMemoryEventBus."""
        from aiokafka.errors import KafkaConnectionError
        try:
            self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
            await self.producer.start()
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                enable_auto_commit=True,
                auto_offset_reset="earliest",
            )
            await self.consumer.start()
            self.logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
            self.connected = True
        except KafkaConnectionError as e:
            self.logger.warning(f"Kafka broker not available: {e}. Running in degraded mode (no broker). Delegating to InMemoryEventBus.")
            self.connected = False
            self.fallback_bus = InMemoryEventBus()
        except KafkaError as e:
            self.logger.error(f"Kafka connection failed: {e}")
            self.connected = False
            self.fallback_bus = InMemoryEventBus()
            raise

    async def publish(self, message: bytes, key: Optional[bytes] = None):
        """Async: Publish a message to the Kafka topic. Delegate to fallback bus in degraded mode."""
        if not self.connected:
            if self.fallback_bus:
                return await self.fallback_bus.publish(message)
            self.logger.warning("KafkaEventBus in degraded mode: publish() is a no-op (no broker connected). Message not sent.")
            return
        if not self.producer:
            raise RuntimeError("Producer not connected. Call connect() first.")
        try:
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
            self.logger.warning("KafkaEventBus in degraded mode: subscribe() is a no-op (no broker connected).")
            return
        if not self.consumer:
            raise RuntimeError("Consumer not connected. Call connect() with group_id.")
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[KafkaEventBus] Starting async subscribe loop for topics: {self.topics}, group_id: {self.group_id}",
            make_log_context(node_id="node_kafka_event_bus")
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
                    make_log_context(node_id="node_kafka_event_bus")
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