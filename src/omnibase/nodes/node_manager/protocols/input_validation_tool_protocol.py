from typing import Optional, Protocol, Tuple

from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.node_manager.v1_0_0.models.state import NodeManagerInputState, NodeManagerOutputState


class InputValidationToolProtocol(Protocol):
    def validate_input_state(
        self, input_state: dict, semver: SemVerModel, event_bus
    ) -> Tuple[Optional[NodeManagerInputState], Optional[NodeManagerOutputState]]:
        """
        Validates the input_state dict against NodeManagerInputState.
        Returns (state, None) if valid, or (None, error_output) if invalid.
        """
        ...
