from typing import Protocol

from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import (
    KafkaHealthCheckResult,
    ModelEventBusConfig,
)


class ToolHealthCheckProtocol(Protocol):
    """
    Protocol for health check tool for the Kafka event bus node.
    Accepts a strongly-typed ModelEventBusConfig and returns a KafkaHealthCheckResult.
    """

    def health_check(self, config: ModelEventBusConfig) -> KafkaHealthCheckResult:
        """
        Perform a health check on the Kafka event bus backend.
        Args:
            config: ModelEventBusConfig
        Returns:
            KafkaHealthCheckResult: The result of the health check
        """
        ...
