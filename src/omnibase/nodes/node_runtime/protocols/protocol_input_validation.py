# [ONEX_PROMPT] This protocol defines the input validation interface for {NODE_NAME}. Replace all tokens and customize validation logic as needed for your node.
"""
Protocol for input validation tool for {NODE_NAME} node.
This protocol defines the interface for input validation logic, to be implemented and injected via the registry.
"""

from typing import Protocol, Tuple
from pydantic import BaseModel

from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.{NODE_NAME}.v1_0_0.models.state import {NODE_CLASS}InputState, {NODE_CLASS}OutputState

# [ONEX_PROMPT] Rename and implement this protocol for your node's input validation logic.
class Protocol{NODE_NAME}InputValidation(Protocol):
    """
    [ONEX_PROMPT] Document the purpose and requirements for input validation for {NODE_NAME}.
    Protocol for input validation tool for {NODE_NAME} node.
    Implementations should validate the input state and return a validated model or raise a validation error.
    """
    def validate_input(self, input_state: BaseModel) -> BaseModel:
        """
        [ONEX_PROMPT] Implement input validation logic for {NODE_NAME}. Return a validated model or raise a ValidationError.
        Validate the input state for {NODE_NAME} node.
        Args:
            input_state (BaseModel): The input state model to validate.
        Returns:
            BaseModel: The validated (and possibly normalized) input state.
        Raises:
            ValidationError: If the input is invalid.
        """
        ...
