from typing import Optional, Protocol

from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import (
    ModelKafkaEventBusConfig,
)
from omnibase.protocol.protocol_event_bus import ProtocolEventBus


class ToolBackendSelectionProtocol(Protocol):
    """
    Protocol for backend selection tool for the Kafka event bus node.
    Accepts a strongly-typed ModelKafkaEventBusConfig and returns a ProtocolEventBus instance.
    """

    def select_event_bus(
        self, config: Optional[ModelKafkaEventBusConfig] = None, logger=None
    ) -> ProtocolEventBus:
        """
        Select and instantiate the appropriate event bus backend (Kafka or InMemory) based on config.
        Args:
            config: ModelKafkaEventBusConfig or None
            logger: Optional logger for diagnostics (optional, may be None)
        Returns:
            ProtocolEventBus: The selected event bus instance
        """
        ...
