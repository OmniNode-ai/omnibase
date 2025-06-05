from typing import Optional, Callable, Any
import logging
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import KafkaEventBusConfigModel
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable
from omnibase.model.model_onex_event import OnexEvent
import typing
import asyncio
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
        self.group_id = config.group_id
        self.connected = False  # Track connection status
        # TODO: Use all config fields for advanced setup (security, partitions, etc.)

    async def connect(self):
        """Async: Establish connection to Kafka cluster. If no broker is available, degrade gracefully and set self.connected = False. Temporary bridge to sync kafka-python."""
        try:
            self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
            if self.group_id:
                self.consumer = KafkaConsumer(
                    self.topics,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=self.group_id,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True
                )
            self.logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
            self.connected = True
        except NoBrokersAvailable as e:
            self.logger.warning(f"Kafka broker not available: {e}. Running in degraded mode (no broker).")
            self.connected = False
        except KafkaError as e:
            self.logger.error(f"Kafka connection failed: {e}")
            self.connected = False
            raise

    async def publish(self, message: bytes, key: Optional[bytes] = None):
        """Async: Publish a message to the Kafka topic. No-op in degraded mode."""
        if not self.connected:
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
        """Async: Subscribe to the Kafka topic and process messages with the given callback. No-op in degraded mode."""
        if not self.connected:
            self.logger.warning("KafkaEventBus in degraded mode: subscribe() is a no-op (no broker connected).")
            return
        if not self.consumer:
            raise RuntimeError("Consumer not connected. Call connect() with group_id.")
        try:
            for msg in self.consumer:
                self.logger.info(f"Received message: {msg}")
                on_message(msg)
        except KafkaError as e:
            self.logger.error(f"Kafka subscribe failed: {e}")
            raise

    async def close(self):
        """Async: Close Kafka producer and consumer connections. Temporary bridge to sync kafka-python."""
        if self.producer:
            self.producer.close()
        if self.consumer:
            self.consumer.close()
        self.logger.info("Kafka connections closed.")

    async def health_check(self) -> dict:
        """
        Async: Check Kafka broker reachability and return health status/metrics. Temporary bridge to sync kafka-python.
        Returns:
            dict: {"status": "ok"|"error", "error": str|None, "bootstrap_servers": list, "topics": list}
        """
        try:
            # Attempt to connect to Kafka cluster
            producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
            # Optionally, list topics (requires admin client for full support)
            status = "ok"
            error = None
            producer.close()
        except Exception as e:
            status = "error"
            error = str(e)
        return {
            "status": status,
            "error": error,
            "bootstrap_servers": self.bootstrap_servers,
            "topics": self.topics,
        }

# TODO: Add partitioning, ack, error handling, and advanced features as per checklist. 