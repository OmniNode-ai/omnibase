from pathlib import Path

def tool_generate_introspection(contract_path: Path, output_path: Path):
    """
    Generate introspection.py from contract.yaml using NodeIntrospectionResponse model.
    Args:
        contract_path: Path to the contract.yaml file
        output_path: Path to write the generated introspection.py file
    """
    import yaml
    with open(contract_path, "r") as f:
        contract = yaml.safe_load(f)
    node_dir = output_path.parent.parent
    introspection_path = node_dir / "introspection.py"
    header = (
        "# AUTO-GENERATED FILE. DO NOT EDIT.\n"
        "# Generated from contract.yaml\n"
        "# To regenerate: run the node_manager codegen orchestrator.\n"
    )
    code = f"""{header}
from omnibase.model.model_node_introspection import NodeIntrospectionResponse, NodeMetadataModel, ContractModel, StateModelsModel, ErrorCodesModel, DependenciesModel, NodeCapabilityEnum\n\ndef get_node_introspection_response() -> NodeIntrospectionResponse:\n    # TODO: Populate with real values from contract and codegen\n    return NodeIntrospectionResponse(\n        node_metadata=NodeMetadataModel(\n            name=contract.get('node_name', ''),\n            version=contract.get('version', ''),\n            description=contract.get('description', ''),\n            author=contract.get('author', ''),\n            schema_version=contract.get('schema_version', ''),\n        ),\n        contract=ContractModel(\n            input_state_schema=contract.get('input_state_schema', ''),\n            output_state_schema=contract.get('output_state_schema', ''),\n            cli_interface=contract.get('cli_interface', {{}}),\n            protocol_version=contract.get('protocol_version', ''),\n        ),\n        state_models=None,  # TODO\n        error_codes=None,   # TODO\n        dependencies=None,  # TODO\n        capabilities=[],\n        introspection_version=\"1.0.0\",\n    )\n"""
    with open(introspection_path, "w") as f:
        f.write(code)
    print(f"[INFO] Generated introspection.py at {introspection_path}") 