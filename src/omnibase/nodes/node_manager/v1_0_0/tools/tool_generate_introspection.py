from pathlib import Path
import yaml
import re
import toml

def tool_generate_introspection(contract_path: Path, output_path: Path):
    """
    Generate introspection.py from contract.yaml using NodeIntrospectionResponse model.
    Args:
        contract_path: Path to the contract.yaml file
        output_path: Path to write the generated introspection.py file
    """
    # Load contract
    with open(contract_path, "r") as f:
        contract = yaml.safe_load(f)
    node_dir = output_path.parent.parent
    introspection_path = node_dir / "introspection.py"
    # Load pyproject.toml for dependencies
    pyproject = toml.load("pyproject.toml")
    python_version = pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {}).get("python", ">=3.11,<3.12")
    runtime_deps = [k for k in pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {}).keys() if k != "python"]
    # Load state.py for model class names
    state_path = node_dir / "models" / "state.py"
    with open(state_path, "r") as f:
        state_code = f.read()
    input_model_match = re.search(r'class (\w+InputState)\(', state_code)
    output_model_match = re.search(r'class (\w+OutputState)\(', state_code)
    input_model = input_model_match.group(1) if input_model_match else "InputState"
    output_model = output_model_match.group(1) if output_model_match else "OutputState"
    # Load error_codes.py for error code enum
    error_codes_path = node_dir / "error_codes.py"
    error_codes = []
    if error_codes_path.exists():
        with open(error_codes_path, "r") as f:
            for line in f:
                m = re.match(r'\s+(\w+) = ', line)
                if m:
                    error_codes.append(m.group(1))
    # Compose static introspection.py
    header = (
        "# AUTO-GENERATED FILE. DO NOT EDIT.\n"
        "# Generated from contract.yaml\n"
        "# To regenerate: run the node_manager codegen orchestrator.\n"
    )
    code = f'''{header}
from omnibase.model.model_node_introspection import NodeIntrospectionResponse, NodeMetadataModel, ContractModel, StateModelsModel, StateModelModel, StateFieldModel, ErrorCodesModel, ErrorCodeModel, DependenciesModel, NodeCapabilityEnum\n\ndef get_node_introspection_response() -> NodeIntrospectionResponse:\n    return NodeIntrospectionResponse(\n        node_metadata=NodeMetadataModel(\n            name="{contract.get('node_name', '')}",\n            version="{contract.get('node_version', contract.get('contract_version', ''))}",\n            description="{contract.get('contract_description', '')}",\n            author="OmniNode Team",\n            schema_version="{contract.get('contract_version', '')}",\n        ),\n        contract=ContractModel(\n            input_state_schema="input_state",\n            output_state_schema="output_state",\n            cli_interface=None,  # TODO: Populate CLI interface if available\n            protocol_version="1.0.0",\n        ),\n        state_models=StateModelsModel(\n            input=StateModelModel(\n                class_name="{input_model}",\n                schema_version="{contract.get('contract_version', '')}",\n                fields=[],  # TODO: Populate fields from contract/input_state\n                schema_file=None,\n            ),\n            output=StateModelModel(\n                class_name="{output_model}",\n                schema_version="{contract.get('contract_version', '')}",\n                fields=[],  # TODO: Populate fields from contract/output_state\n                schema_file=None,\n            ),\n        ),\n        error_codes=ErrorCodesModel(\n            component="{contract.get('node_name', '')}",\n            codes=[ErrorCodeModel(code=code, number=i+1, description="", exit_code=1, category="") for i, code in enumerate({error_codes})],\n            total_codes={len(error_codes)},\n        ) if {bool(error_codes)} else None,\n        dependencies=DependenciesModel(\n            runtime={runtime_deps},\n            optional=[],\n            python_version="{python_version}",\n            external_tools=[],\n        ),\n        capabilities=[NodeCapabilityEnum.SUPPORTS_EVENT_BUS, NodeCapabilityEnum.SUPPORTS_SCHEMA_VALIDATION],\n        introspection_version="1.0.0",\n    )\n'''
    with open(introspection_path, "w") as f:
        f.write(code)
    print(f"[INFO] Generated introspection.py at {introspection_path}") 