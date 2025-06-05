from typing import Protocol
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import KafkaEventBusConfigModel, KafkaHealthCheckResult

class ToolHealthCheckProtocol(Protocol):
    """
    Protocol for health check tool for the Kafka event bus node.
    Accepts a strongly-typed KafkaEventBusConfigModel and returns a KafkaHealthCheckResult.
    """
    def health_check(self, config: KafkaEventBusConfigModel) -> KafkaHealthCheckResult:
        """
        Perform a health check on the Kafka event bus backend.
        Args:
            config: KafkaEventBusConfigModel
        Returns:
            KafkaHealthCheckResult: The result of the health check
        """
        ... 