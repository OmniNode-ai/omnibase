from typing import Protocol, Tuple, Optional
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.state import NodeKafkaEventBusInputState, NodeKafkaEventBusOutputState
from omnibase.model.model_semver import SemVerModel

class InputValidationToolProtocol(Protocol):
    def validate_input_state(
        self,
        input_state: dict,
        semver: SemVerModel,
        event_bus
    ) -> Tuple[Optional[NodeKafkaEventBusInputState], Optional[NodeKafkaEventBusOutputState]]:
        """
        Validates the input_state dict against NodeKafkaEventBusInputState.
        Returns (state, None) if valid, or (None, error_output) if invalid.
        """
        ... 