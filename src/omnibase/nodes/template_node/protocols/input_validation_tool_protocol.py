from typing import Optional, Protocol, Tuple

from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.template_node.v1_0_0.models.state import (
    TemplateNodeInputState,
    TemplateNodeOutputState,
)


class InputValidationToolProtocol(Protocol):
    def validate_input_state(
        self, input_state: dict, semver: SemVerModel, event_bus
    ) -> Tuple[Optional[TemplateNodeInputState], Optional[TemplateNodeOutputState]]:
        """
        Validates the input_state dict against TemplateNodeInputState.
        Returns (state, None) if valid, or (None, error_output) if invalid.
        """
        ...
