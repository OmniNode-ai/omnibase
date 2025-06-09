from typing import Optional, Protocol, Tuple

from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.node_model_generator.v1_0_0.models.model_generator_state import NodeModelGeneratorInputState, NodeModelGeneratorOutputState


class InputValidationToolProtocol(Protocol):
    def validate_input_state(
        self, input_state: dict, semver: SemVerModel, event_bus
    ) -> Tuple[Optional[NodeModelGeneratorInputState], Optional[NodeModelGeneratorOutputState]]:
        """
        Validates the input_state dict against NodeModelGeneratorInputState.
        Returns (state, None) if valid, or (None, error_output) if invalid.
        """
        ...
