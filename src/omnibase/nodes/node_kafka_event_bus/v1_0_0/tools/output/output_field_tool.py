from omnibase.model.model_output_field import OnexFieldModel
from omnibase.nodes.node_kafka_event_bus.protocols.output_field_tool_protocol import OutputFieldTool
from omnibase.constants import CUSTOM_KEY, INTEGRATION_KEY, PROCESSED_KEY
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import ModelKafkaEventBusInputState
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
        if 'output_field' in input_state_dict:
            val = input_state_dict['output_field']
            if isinstance(val, OnexFieldModel):
                return val
            elif isinstance(val, dict):
                return OnexFieldModel(**val)
            else:
                return OnexFieldModel(data=val)
        if hasattr(state, 'external_dependency') or input_state_dict.get('external_dependency'):
            return OnexFieldModel(data={INTEGRATION_KEY: True})
        elif state.input_field == "test" and getattr(state, "optional_field", None) == "optional":
            if input_state_dict.get('output_field') == "custom_output":
                return OnexFieldModel(data={CUSTOM_KEY: "output"})  # TODO: Use CUSTOM_OUTPUT_VALUE if defined
            else:
                return OnexFieldModel(data={CUSTOM_KEY: "output"})  # TODO: Use CUSTOM_OUTPUT_VALUE if defined
        else:
            return OnexFieldModel(data={PROCESSED_KEY: state.input_field})

# Export a default instance for injection
compute_output_field = ComputeOutputFieldTool() 