# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml with complete metadata extraction
# To regenerate: run the node_manager codegen orchestrator.

from omnibase.model.model_node_introspection import NodeIntrospectionResponse, NodeMetadataModel, ContractModel, StateModelsModel, StateModelModel, StateFieldModel, ErrorCodesModel, ErrorCodeModel, DependenciesModel, NodeCapabilityEnum

def get_node_introspection_response() -> NodeIntrospectionResponse:
    return NodeIntrospectionResponse(
        node_metadata=NodeMetadataModel(
            name="node_manager",
            version="1.0.0",
            description="State contract for node_manager",
            author="OmniNode Team",
            schema_version="1.0.0",
        ),
        contract=ContractModel(
            input_state_schema="input_state",
            output_state_schema="output_state",
            cli_interface={
            "command_name": "node_manager",
            "description": "State contract for node_manager",
            "parameters": [{'name': 'version', 'type': 'string', 'description': 'Schema version for input state', 'required': True, 'default': None, 'help_text': 'Schema version for input state'}, {'name': 'input_field', 'type': 'string', 'description': 'Required input field for node_manager', 'required': True, 'default': None, 'help_text': 'Required input field for node_manager'}, {'name': 'optional_field', 'type': 'string', 'description': 'Optional input field for node_manager', 'required': False, 'default': None, 'help_text': 'Optional input field for node_manager'}, {'name': 'external_dependency', 'type': 'boolean', 'description': 'Optional flag to simulate integration context for scenario-driven testing', 'required': False, 'default': None, 'help_text': 'Optional flag to simulate integration context for scenario-driven testing'}],
            "examples": ['poetry run onex run node_manager --help', 'poetry run onex run node_manager --introspect']
        },
            protocol_version="1.0.0",
        ),
        state_models=StateModelsModel(
            input=StateModelModel(
                class_name="NodeManagerInputState",
                schema_version="1.0.0",
                fields=[
                StateFieldModel(name="version", type="string", description="Schema version for input state", required=True),
                StateFieldModel(name="input_field", type="string", description="Required input field for node_manager", required=True),
                StateFieldModel(name="optional_field", type="string", description="Optional input field for node_manager", required=False),
                StateFieldModel(name="external_dependency", type="boolean", description="Optional flag to simulate integration context for scenario-driven testing", required=False),
                StateFieldModel(name="event_id", type="string", description="Unique event identifier (UUID)", required=False),
                StateFieldModel(name="correlation_id", type="string", description="Correlation ID for tracing requests/events", required=False),
                StateFieldModel(name="node_name", type="string", description="Name of the node processing the event", required=False),
                StateFieldModel(name="node_version", type="string", description="Version of the node", required=False),
                StateFieldModel(name="timestamp", type="string", description="ISO8601 timestamp of the event", required=False)
            ],
                schema_file="models/state.py",
            ),
            output=StateModelModel(
                class_name="NodeManagerOutputState",
                schema_version="1.0.0",
                fields=[
                StateFieldModel(name="version", type="string", description="Schema version for output state (matches input)", required=True),
                StateFieldModel(name="status", type="string", description="Execution status", required=True),
                StateFieldModel(name="message", type="string", description="Human-readable result message", required=True),
                StateFieldModel(name="output_field", type="string", description="", required=False),
                StateFieldModel(name="event_id", type="string", description="Unique event identifier (UUID)", required=False),
                StateFieldModel(name="correlation_id", type="string", description="Correlation ID for tracing requests/events", required=False),
                StateFieldModel(name="node_name", type="string", description="Name of the node processing the event", required=False),
                StateFieldModel(name="node_version", type="string", description="Version of the node", required=False),
                StateFieldModel(name="timestamp", type="string", description="ISO8601 timestamp of the event", required=False),
                StateFieldModel(name="schemas_generated", type="array", description="List of schema files that were generated (for schema generation operations)", required=False),
                StateFieldModel(name="output_directory", type="string", description="Directory where schemas were generated (for schema generation operations)", required=False),
                StateFieldModel(name="total_schemas", type="integer", description="Total number of schemas generated (for schema generation operations)", required=False)
            ],
                schema_file="models/state.py",
            ),
        ),
        error_codes=None,
        dependencies=DependenciesModel(
            runtime=['pyyaml', 'jsonschema', 'pydantic', 'typer', 'typing-extensions', 'click', 'pathspec', 'pyzmq', 'nats-py', 'kafka-python', 'aiokafka', 'toml', 'python-dotenv'],
            optional=[],
            python_version=">=3.11,<3.12",
            external_tools=[],
        ),
        capabilities=[NodeCapabilityEnum.SUPPORTS_SCHEMA_VALIDATION, NodeCapabilityEnum.SUPPORTS_EVENT_BUS, NodeCapabilityEnum.SUPPORTS_CLI, NodeCapabilityEnum.SUPPORTS_EXTERNAL_DEPENDENCIES],
        introspection_version="1.0.0",
    )
