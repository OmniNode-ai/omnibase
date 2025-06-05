from typing import Protocol, Tuple, Optional
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import ModelKafkaEventBusInputState, ModelKafkaEventBusOutputState
from omnibase.model.model_semver import SemVerModel

class InputValidationToolProtocol(Protocol):
    def validate_input_state(
        self,
        input_state: dict,
        semver: SemVerModel,
        event_bus
    ) -> Tuple[Optional[ModelKafkaEventBusInputState], Optional[ModelKafkaEventBusOutputState]]:
        """
        Validates the input_state dict against ModelKafkaEventBusInputState.
        Returns (state, None) if valid, or (None, error_output) if invalid.
        """
        ... 