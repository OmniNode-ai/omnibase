from typing import Optional, Protocol, Tuple

from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import (
    ModelEventBusInputState,
    ModelEventBusOutputState,
)


class InputValidationToolProtocol(Protocol):
    def validate_input_state(
        self, input_state: dict, semver: SemVerModel, event_bus
    ) -> Tuple[
        Optional[ModelEventBusInputState], Optional[ModelEventBusOutputState]
    ]:
        """
        Validates the input_state dict against ModelEventBusInputState.
        Returns (state, None) if valid, or (None, error_output) if invalid.
        """
        ...
