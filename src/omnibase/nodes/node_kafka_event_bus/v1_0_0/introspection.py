# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
# To regenerate: run the node_manager codegen orchestrator.

from omnibase.model.model_node_introspection import NodeIntrospectionResponse, NodeMetadataModel, ContractModel, StateModelsModel, ErrorCodesModel, DependenciesModel, NodeCapabilityEnum

def get_node_introspection_response() -> NodeIntrospectionResponse:
    # TODO: Populate with real values from contract and codegen
    return NodeIntrospectionResponse(
        node_metadata=NodeMetadataModel(
            name=contract.get('node_name', ''),
            version=contract.get('version', ''),
            description=contract.get('description', ''),
            author=contract.get('author', ''),
            schema_version=contract.get('schema_version', ''),
        ),
        contract=ContractModel(
            input_state_schema=contract.get('input_state_schema', ''),
            output_state_schema=contract.get('output_state_schema', ''),
            cli_interface=contract.get('cli_interface', {}),
            protocol_version=contract.get('protocol_version', ''),
        ),
        state_models=None,  # TODO
        error_codes=None,   # TODO
        dependencies=None,  # TODO
        capabilities=[],
        introspection_version="1.0.0",
    )
