from typing import Protocol

from omnibase.model.model_output_field import OnexFieldModel

# Protocol for node_parity_validator output field tool
class OutputFieldTool(Protocol):
    def __call__(self, state, input_state_dict) -> OnexFieldModel: ...
