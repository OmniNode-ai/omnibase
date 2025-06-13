# [ONEX_PROMPT] This protocol defines the output field interface for {NODE_NAME}. Replace all tokens and customize output field logic as needed for your node.
"""
Protocol for output field tool for {NODE_NAME} node.
Defines the interface for generating output field models from state and input.
"""

from typing import Protocol
from pydantic import BaseModel
from omnibase.model.model_output_field import OnexFieldModel

# [ONEX_PROMPT] Rename and implement this protocol for your node's output field logic.
class Protocol{NODE_NAME}OutputField(Protocol):
    """
    [ONEX_PROMPT] Document the purpose and requirements for output field generation for {NODE_NAME}.
    Protocol for output field tool for {NODE_NAME} node.
    Implementations should generate an OnexFieldModel from the node's state and input.
    """
    def __call__(self, state: BaseModel, input_state: BaseModel) -> OnexFieldModel:
        """
        [ONEX_PROMPT] Implement output field logic for {NODE_NAME}. Return an OnexFieldModel based on state and input.
        """
        ...
