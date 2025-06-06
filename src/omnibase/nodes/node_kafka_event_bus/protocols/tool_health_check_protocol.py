from typing import Protocol

from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import (
    KafkaHealthCheckResult,
    ModelKafkaEventBusConfig,
)


class ToolHealthCheckProtocol(Protocol):
    """
    Protocol for health check tool for the Kafka event bus node.
    Accepts a strongly-typed ModelKafkaEventBusConfig and returns a KafkaHealthCheckResult.
    """

    def health_check(self, config: ModelKafkaEventBusConfig) -> KafkaHealthCheckResult:
        """
        Perform a health check on the Kafka event bus backend.
        Args:
            config: ModelKafkaEventBusConfig
        Returns:
            KafkaHealthCheckResult: The result of the health check
        """
        ...
