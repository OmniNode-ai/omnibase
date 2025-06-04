from typing import Protocol
from omnibase.model.model_output_field import OnexFieldModel

class OutputFieldTool(Protocol):
    def __call__(self, state, input_state_dict) -> OnexFieldModel: ... 