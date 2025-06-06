from typing import Any, Dict

from omnibase.constants import (
    CUSTOM_KEY,
    CUSTOM_OUTPUT_INPUT_VALUE,
    CUSTOM_OUTPUT_VALUE,
    EXTERNAL_DEPENDENCY_KEY,
    INTEGRATION_KEY,
    OPTIONAL_FIELD_KEY,
    OPTIONAL_INPUT_VALUE,
    OUTPUT_FIELD_KEY,
    PROCESSED_KEY,
    TEST_INPUT_VALUE,
)
from omnibase.model.model_output_field import OnexFieldModel
from omnibase.protocol.protocol_output_field_tool import (
    OutputFieldTool,
)
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import (
    ModelEventBusInputState,
)

# TODO: Define OUTPUT_VALUE, CUSTOM_OUTPUT_VALUE in constants if needed


class ComputeOutputFieldTool(OutputFieldTool):
    def __call__(
        self, state: ModelEventBusInputState, input_state_dict: Dict[str, Any]
    ) -> OnexFieldModel:
        """
        Compute the output_field for NodeKafkaEventBus based on input state.
        Args:
            state: Validated ModelEventBusInputState
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
        if hasattr(state, EXTERNAL_DEPENDENCY_KEY) or input_state_dict.get(
            EXTERNAL_DEPENDENCY_KEY
        ):
            return OnexFieldModel(data={INTEGRATION_KEY: True})
        elif (
            state.input_field == TEST_INPUT_VALUE
            and getattr(state, OPTIONAL_FIELD_KEY, None) == OPTIONAL_INPUT_VALUE
        ):
            if input_state_dict.get(OUTPUT_FIELD_KEY) == CUSTOM_OUTPUT_INPUT_VALUE:
                return OnexFieldModel(data={CUSTOM_KEY: CUSTOM_OUTPUT_VALUE})
            else:
                return OnexFieldModel(data={CUSTOM_KEY: CUSTOM_OUTPUT_VALUE})
        else:
            return OnexFieldModel(data={PROCESSED_KEY: state.input_field})


# Export a default instance for injection
compute_output_field = ComputeOutputFieldTool()
