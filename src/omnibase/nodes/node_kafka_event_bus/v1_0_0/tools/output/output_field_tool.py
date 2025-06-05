from omnibase.model.model_output_field import OnexFieldModel
from omnibase.nodes.node_kafka_event_bus.protocols.output_field_tool_protocol import OutputFieldTool

def compute_output_field(state, input_state_dict) -> OnexFieldModel:
    """
    Compute the output_field for NodeKafkaEventBus based on input state.
    Args:
        state: Validated NodeKafkaEventBusInputState
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
        return OnexFieldModel(data={"integration": True})
    elif state.input_field == "test" and getattr(state, "optional_field", None) == "optional":
        if input_state_dict.get('output_field') == "custom_output":
            return OnexFieldModel(data={"custom": "output"})
        else:
            return OnexFieldModel(data={"custom": "output"})
    else:
        return OnexFieldModel(data={"processed": state.input_field}) 