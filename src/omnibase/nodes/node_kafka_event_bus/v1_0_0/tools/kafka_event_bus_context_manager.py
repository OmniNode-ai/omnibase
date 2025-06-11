from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import KafkaEventBus
from omnibase.model.model_event_bus_config import ModelEventBusConfig
from omnibase.enums import LogLevelEnum
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import make_log_context, NODE_KAFKA_EVENT_BUS_ID
from omnibase.protocol.protocol_event_bus_context_manager import ProtocolEventBusContextManager

class KafkaEventBusContextManager(ProtocolEventBusContextManager[KafkaEventBus]):
    """
    Async context manager for KafkaEventBus lifecycle management.
    Implements ProtocolEventBusContextManager.
    Handles connect, structured logging, and clean shutdown.
    Logs all lifecycle transitions for producer and consumer objects.
    """
    def __init__(self, config: ModelEventBusConfig):
        self.config = config
        self.bus = KafkaEventBus(config)
        # Log initialization
        emit_log_event_sync(
            LogLevelEnum.INFO,
            "[KafkaEventBusContextManager] Initialized context manager (producer/consumer not connected yet)",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
        )

    async def __aenter__(self) -> KafkaEventBus:
        # Log connection start
        emit_log_event_sync(
            LogLevelEnum.INFO,
            "[KafkaEventBusContextManager] Entering context, connecting producer/consumer...",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
        )
        await self.bus.connect()
        # Log connection success
        emit_log_event_sync(
            LogLevelEnum.INFO,
            "[KafkaEventBusContextManager] Producer/consumer connected.",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
        )
        # Optionally log current state of producer/consumer
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[KafkaEventBusContextManager] Producer: {getattr(self.bus, 'producer', None)}, Consumer: {getattr(self.bus, 'consumer', None)}",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
        )
        return self.bus

    async def __aexit__(self, exc_type, exc, tb) -> None:
        # Log shutdown start
        emit_log_event_sync(
            LogLevelEnum.INFO,
            "[KafkaEventBusContextManager] Exiting context, closing producer/consumer...",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
        )
        await self.bus.close()
        # Log shutdown complete
        emit_log_event_sync(
            LogLevelEnum.INFO,
            "[KafkaEventBusContextManager] Producer/consumer closed.",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
        )
        # Optionally log deletion/cleanup
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[KafkaEventBusContextManager] Producer: {getattr(self.bus, 'producer', None)}, Consumer: {getattr(self.bus, 'consumer', None)} after close",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
        ) 