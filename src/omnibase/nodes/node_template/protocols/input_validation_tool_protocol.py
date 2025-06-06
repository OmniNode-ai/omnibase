from typing import Optional, Protocol, Tuple

from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.node_template.v1_0_0.models.state import (
    NodeTemplateInputState,
    NodeTemplateOutputState,
)


class InputValidationToolProtocol(Protocol):
    def validate_input_state(
        self, input_state: dict, semver: SemVerModel, event_bus
    ) -> Tuple[Optional[NodeTemplateInputState], Optional[NodeTemplateOutputState]]:
        """
        Validates the input_state dict against NodeTemplateInputState.
        Returns (state, None) if valid, or (None, error_output) if invalid.
        """
        ...
