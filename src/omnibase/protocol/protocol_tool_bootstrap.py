from typing import Protocol

from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.model_kafka_event_bus_bootstrap_result import (
    ModelKafkaEventBusBootstrapResult,
)
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import (
    ModelKafkaEventBusConfig,
)


class ToolBootstrapProtocol(Protocol):
    """
    Protocol for bootstrap tool for the Kafka event bus node.
    Accepts a strongly-typed ModelKafkaEventBusConfig and returns a ModelKafkaEventBusBootstrapResult.
    """

    def bootstrap_kafka_cluster(
        self, config: ModelKafkaEventBusConfig
    ) -> ModelKafkaEventBusBootstrapResult:
        """
        Perform bootstrap initialization for the Kafka cluster.
        Args:
            config: ModelKafkaEventBusConfig
        Returns:
            ModelKafkaEventBusBootstrapResult
        """
        ...
