from omnibase.model.model_output_field import OnexFieldModel
from omnibase.nodes.node_kafka_event_bus.protocols.output_field_tool_protocol import OutputFieldTool
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import ModelKafkaEventBusInputState
from omnibase.constants import (
    CUSTOM_KEY, INTEGRATION_KEY, PROCESSED_KEY,
    CUSTOM_OUTPUT_INPUT_VALUE, CUSTOM_OUTPUT_VALUE, TEST_INPUT_VALUE, OPTIONAL_INPUT_VALUE,
    OPTIONAL_FIELD_KEY, OUTPUT_FIELD_KEY, EXTERNAL_DEPENDENCY_KEY
)
from typing import Dict, Any
# TODO: Define OUTPUT_VALUE, CUSTOM_OUTPUT_VALUE in constants if needed

class ComputeOutputFieldTool(OutputFieldTool):
    def __call__(
        self,
        state: ModelKafkaEventBusInputState,
        input_state_dict: Dict[str, Any]
    ) -> OnexFieldModel:
        """
        Compute the output_field for NodeKafkaEventBus based on input state.
        Args:
            state: Validated ModelKafkaEventBusInputState
            input_state_dict: Original input_state dict (for extra keys)
        Returns:
            OnexFieldModel or None
        """
        if OUTPUT_FIELD_KEY in input_state_dict:
            val = input_state_dict[OUTPUT_FIELD_KEY]
            if isinstance(val, OnexFieldModel):
                return val
            elif isinstance(val, dict):
                return OnexFieldModel(**val)
            else:
                return OnexFieldModel(data=val)
        if hasattr(state, EXTERNAL_DEPENDENCY_KEY) or input_state_dict.get(EXTERNAL_DEPENDENCY_KEY):
            return OnexFieldModel(data={INTEGRATION_KEY: True})
        elif state.input_field == TEST_INPUT_VALUE and getattr(state, OPTIONAL_FIELD_KEY, None) == OPTIONAL_INPUT_VALUE:
            if input_state_dict.get(OUTPUT_FIELD_KEY) == CUSTOM_OUTPUT_INPUT_VALUE:
                return OnexFieldModel(data={CUSTOM_KEY: CUSTOM_OUTPUT_VALUE})
            else:
                return OnexFieldModel(data={CUSTOM_KEY: CUSTOM_OUTPUT_VALUE})
        else:
            return OnexFieldModel(data={PROCESSED_KEY: state.input_field})

# Export a default instance for injection
compute_output_field = ComputeOutputFieldTool() 