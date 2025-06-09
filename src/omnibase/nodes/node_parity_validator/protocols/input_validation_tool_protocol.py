from typing import Optional, Protocol, Tuple

from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.node_parity_validator.v1_0_0.models.state import (
    ParityValidatorInputState,
    ParityValidatorOutputState,
)


class InputValidationToolProtocol(Protocol):
    def validate_input_state(
        self, input_state: dict, semver: SemVerModel, event_bus
    ) -> Tuple[Optional[ParityValidatorInputState], Optional[ParityValidatorOutputState]]:
        """
        Validates the input_state dict against ParityValidatorInputState.
        Returns (state, None) if valid, or (None, error_output) if invalid.
        """
        ...
