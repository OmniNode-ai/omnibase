from typing import Protocol

from omnibase.model.model_event_bus_bootstrap_result import ModelEventBusBootstrapResult
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import (
    ModelEventBusConfig,
)


class ToolBootstrapProtocol(Protocol):
    """
    Protocol for bootstrap tool for the Kafka event bus node.
    Accepts a strongly-typed ModelEventBusConfig and returns a ModelEventBusBootstrapResult.
    """

    def bootstrap_kafka_cluster(
        self, config: ModelEventBusConfig
    ) -> ModelEventBusBootstrapResult:
        """
        Perform bootstrap initialization for the Kafka cluster.
        Args:
            config: ModelEventBusConfig
        Returns:
            ModelEventBusBootstrapResult
        """
        ...
