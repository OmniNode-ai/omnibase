# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
# To regenerate: run the node_manager codegen orchestrator.

from omnibase.model.model_node_introspection import NodeIntrospectionResponse, NodeMetadataModel, ContractModel, StateModelsModel, StateModelModel, StateFieldModel, ErrorCodesModel, ErrorCodeModel, DependenciesModel, NodeCapabilityEnum

def get_node_introspection_response() -> NodeIntrospectionResponse:
    return NodeIntrospectionResponse(
        node_metadata=NodeMetadataModel(
            name="node_kafka_event_bus_node",
            version="1.0.0",
            description="State contract for node_kafka_event_bus_node",
            author="OmniNode Team",
            schema_version="1.0.0",
        ),
        contract=ContractModel(
            input_state_schema="input_state",
            output_state_schema="output_state",
            cli_interface=None,  # TODO: Populate CLI interface if available
            protocol_version="1.0.0",
        ),
        state_models=StateModelsModel(
            input=StateModelModel(
                class_name="NodeKafkaEventBusNodeInputState",
                schema_version="1.0.0",
                fields=[],  # TODO: Populate fields from contract/input_state
                schema_file=None,
            ),
            output=StateModelModel(
                class_name="NodeKafkaEventBusNodeOutputState",
                schema_version="1.0.0",
                fields=[],  # TODO: Populate fields from contract/output_state
                schema_file=None,
            ),
        ),
        error_codes=ErrorCodesModel(
            component="node_kafka_event_bus_node",
            codes=[ErrorCodeModel(code=code, number=i+1, description="", exit_code=1, category="") for i, code in enumerate(['BACKEND_UNAVAILABLE', 'CONNECTION_FAILED', 'MESSAGE_PUBLISH_FAILED', 'MESSAGE_CONSUME_FAILED', 'TIMEOUT_EXCEEDED', 'CONFIGURATION_ERROR', 'HANDLER_NOT_FOUND', 'BOOTSTRAP_FAILED', 'INTEGRATION_ERROR', 'RESOURCE_EXHAUSTED'])],
            total_codes=10,
        ) if True else None,
        dependencies=DependenciesModel(
            runtime=['pyyaml', 'jsonschema', 'pydantic', 'typer', 'typing-extensions', 'click', 'pathspec', 'pyzmq', 'nats-py', 'kafka-python', 'aiokafka', 'toml'],
            optional=[],
            python_version=">=3.11,<3.12",
            external_tools=[],
        ),
        capabilities=[NodeCapabilityEnum.SUPPORTS_EVENT_BUS, NodeCapabilityEnum.SUPPORTS_SCHEMA_VALIDATION],
        introspection_version="1.0.0",
    )
