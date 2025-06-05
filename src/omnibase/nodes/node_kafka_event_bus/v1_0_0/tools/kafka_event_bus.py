from typing import Optional, Callable, Any
import logging
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import KafkaEventBusConfigModel
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable
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
if typing.TYPE_CHECKING:
    from omnibase.protocol.protocol_event_bus import ProtocolEventBus

class KafkaEventBus:
    """
    Canonical Kafka Event Bus implementation for ONEX.
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
        # Add a random suffix to group_id to avoid group contention for debugging
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        self.group_id = f"{config.group_id}-{rand_suffix}"
        self.connected = False  # Track connection status
        self.fallback_bus = None  # InMemoryEventBus for degraded mode
        # TODO: Use all config fields for advanced setup (security, partitions, etc.)
        # Assert producer/consumer are not shared across CLI and node
        # (This is a code-level discipline, not runtime, but we log for traceability)
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[KafkaEventBus] Producer/consumer instantiated for this instance only (id={id(self)})",
            make_log_context(node_id="node_kafka_event_bus")
        )

    async def connect(self):
        """Async: Establish connection to Kafka cluster. If no broker is available, degrade gracefully and delegate to InMemoryEventBus."""
        try:
            self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
            if self.group_id:
                self.consumer = KafkaConsumer(
                    *self.topics,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=self.group_id,
                    enable_auto_commit=True,
                    auto_offset_reset="earliest",
                    # group_instance_id=group_instance_id,  # Uncomment if supported by your Kafka version
                )
                self.consumer.subscribe(self.topics)
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[KafkaEventBus] Consumer assignment after connect: {self.consumer.assignment()}",
                    make_log_context(node_id="node_kafka_event_bus")
                )
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[KafkaEventBus] Consumer topics after subscribe: {self.consumer.topics()}",
                    make_log_context(node_id="node_kafka_event_bus")
                )
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[KafkaEventBus] Consumer subscription after subscribe: {self.consumer.subscription()}",
                    make_log_context(node_id="node_kafka_event_bus")
                )
            self.logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
            self.connected = True
        except NoBrokersAvailable as e:
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
        # Topic/schema validation
        try:
            event = json.loads(message)
            topic = self.topics[0] if isinstance(self.topics, list) else self.topics
            if 'event_type' not in event or 'node_id' not in event:
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"[KafkaEventBus] Invalid event schema on publish: {event}",
                    make_log_context(node_id="node_kafka_event_bus")
                )
            if topic not in self.topics:
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"[KafkaEventBus] Publish to unknown topic: {topic}",
                    make_log_context(node_id="node_kafka_event_bus")
                )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[KafkaEventBus] Exception during topic/schema validation on publish: {e}",
                make_log_context(node_id="node_kafka_event_bus")
            )
        if not self.connected:
            if self.fallback_bus:
                return self.fallback_bus.publish(message)
            self.logger.warning("KafkaEventBus in degraded mode: publish() is a no-op (no broker connected). Message not sent.")
            return
        if not self.producer:
            raise RuntimeError("Producer not connected. Call connect() first.")
        try:
            future = self.producer.send(self.topics, value=message, key=key)
            # TODO: Handle partitioning, acks, and error callbacks
            result = future.get(timeout=10)
            self.logger.info(f"Published message to {self.topics}: {result}")
            return result
        except KafkaError as e:
            self.logger.error(f"Kafka publish failed: {e}")
            raise

    async def subscribe(self, on_message: Callable[[Any], None]):
        """Async: Subscribe to the Kafka topic and process messages with the given callback. Delegate to fallback bus in degraded mode."""
        if not self.connected:
            if self.fallback_bus:
                return self.fallback_bus.subscribe(on_message)
            self.logger.warning("KafkaEventBus in degraded mode: subscribe() is a no-op (no broker connected).")
            return
        if not self.consumer:
            raise RuntimeError("Consumer not connected. Call connect() with group_id.")
        import asyncio
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[KafkaEventBus] Starting subscribe loop in background thread for topics: {self.topics}, group_id: {self.group_id}",
            make_log_context(node_id="node_kafka_event_bus")
        )
        loop = asyncio.get_running_loop()
        def consumer_loop():
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[KafkaEventBus] Entered consumer_loop (thread) for topics: {self.topics}, group_id: {self.group_id}",
                make_log_context(node_id="node_kafka_event_bus")
            )
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[KafkaEventBus] Consumer topics at loop start: {self.consumer.topics()}",
                make_log_context(node_id="node_kafka_event_bus")
            )
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[KafkaEventBus] Consumer subscription at loop start: {self.consumer.subscription()}",
                make_log_context(node_id="node_kafka_event_bus")
            )
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[KafkaEventBus] Consumer assignment at loop start: {self.consumer.assignment()}",
                make_log_context(node_id="node_kafka_event_bus")
            )
            for msg in self.consumer:
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[KafkaEventBus] Received message from topic: {msg.topic}, partition: {msg.partition}, offset: {msg.offset}",
                    make_log_context(node_id="node_kafka_event_bus")
                )
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[KafkaEventBus] Consumer assignment in loop: {self.consumer.assignment()}",
                    make_log_context(node_id="node_kafka_event_bus")
                )
                try:
                    # Topic/schema validation
                    try:
                        event = json.loads(msg.value)
                        topic = msg.topic
                        if 'event_type' not in event or 'node_id' not in event:
                            emit_log_event_sync(
                                LogLevelEnum.ERROR,
                                f"[KafkaEventBus] Invalid event schema on subscribe: {event}",
                                make_log_context(node_id="node_kafka_event_bus")
                            )
                        if topic not in self.topics:
                            emit_log_event_sync(
                                LogLevelEnum.ERROR,
                                f"[KafkaEventBus] Subscribe received message from unknown topic: {topic}",
                                make_log_context(node_id="node_kafka_event_bus")
                            )
                    except Exception as e:
                        emit_log_event_sync(
                            LogLevelEnum.ERROR,
                            f"[KafkaEventBus] Exception during topic/schema validation on subscribe: {e}",
                            make_log_context(node_id="node_kafka_event_bus")
                        )
                    # Handler callback with error guard
                    try:
                        if asyncio.iscoroutinefunction(on_message):
                            asyncio.run_coroutine_threadsafe(on_message(msg), loop)
                        else:
                            on_message(msg)
                    except Exception as cb_exc:
                        emit_log_event_sync(
                            LogLevelEnum.ERROR,
                            f"[KafkaEventBus] Exception in event handler callback: {cb_exc}",
                            make_log_context(node_id="node_kafka_event_bus")
                        )
                except Exception as outer_exc:
                    emit_log_event_sync(
                        LogLevelEnum.ERROR,
                        f"[KafkaEventBus] Exception in subscribe loop: {outer_exc}",
                        make_log_context(node_id="node_kafka_event_bus")
                    )
        await asyncio.to_thread(consumer_loop)

    async def close(self):
        """Async: Close Kafka producer and consumer connections. Delegate to fallback bus in degraded mode."""
        if not self.connected and self.fallback_bus:
            return self.fallback_bus.close()
        if self.producer:
            self.producer.close()
        if self.consumer:
            self.consumer.close()
        self.logger.info("Kafka connections closed.")

    async def health_check(self) -> dict:
        """Async: Check Kafka broker connectivity and topic availability. Never blocks indefinitely."""
        result = {"connected": False, "error": None, "topics": None}
        try:
            # Try to connect producer
            producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
            producer.close()
            # Use KafkaAdminClient to list topics (non-blocking)
            admin = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
            topics = admin.list_topics()
            admin.close()
            result["connected"] = True
            result["topics"] = list(topics)
        except Exception as e:
            result["error"] = str(e)
        return result

# TODO: Add partitioning, ack, error handling, and advanced features as per checklist. 