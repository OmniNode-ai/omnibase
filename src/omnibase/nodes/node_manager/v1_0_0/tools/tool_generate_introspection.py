from pathlib import Path
import yaml
import re
import toml
from typing import List, Dict, Any, Optional

from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context


def extract_state_fields(state_schema: dict) -> List[dict]:
    """Extract field definitions from contract state schema"""
    fields = []
    properties = state_schema.get("properties", {})
    required_fields = set(state_schema.get("required", []))
    
    for field_name, field_def in properties.items():
        field_info = {
            "name": field_name,
            "type": field_def.get("type", "string"),
            "description": field_def.get("description", ""),
            "required": field_name in required_fields,
            "default": field_def.get("default"),
            "enum_values": field_def.get("enum"),
            "format": field_def.get("format"),
            "ref": field_def.get("$ref")
        }
        fields.append(field_info)
    
    return fields


def extract_cli_interface(contract: dict) -> Optional[dict]:
    """Generate CLI interface metadata from contract"""
    input_state = contract.get("input_state", {})
    properties = input_state.get("properties", {})
    required_fields = set(input_state.get("required", []))
    
    # Extract CLI-compatible fields (exclude internal fields)
    cli_fields = []
    excluded_fields = {"event_id", "correlation_id", "node_name", "node_version", "timestamp"}
    
    for field_name, field_def in properties.items():
        if field_name not in excluded_fields:
            cli_field = {
                "name": field_name,
                "type": field_def.get("type", "string"),
                "description": field_def.get("description", ""),
                "required": field_name in required_fields,
                "default": field_def.get("default"),
                "help_text": field_def.get("description", f"Input parameter: {field_name}")
            }
            cli_fields.append(cli_field)
    
    if cli_fields:
        return {
            "command_name": contract.get("node_name", "node"),
            "description": contract.get("contract_description", ""),
            "parameters": cli_fields,
            "examples": [
                f"poetry run onex run {contract.get('node_name', 'node')} --help",
                f"poetry run onex run {contract.get('node_name', 'node')} --introspect"
            ]
        }
    
    return None


def extract_error_codes_with_metadata(contract: dict) -> List[dict]:
    """Extract error codes with full metadata"""
    error_codes = []
    error_section = contract.get("error_codes")
    
    if isinstance(error_section, list):
        # Simple list format
        for i, code in enumerate(error_section):
            error_codes.append({
                "code": code,
                "number": i + 1,
                "description": f"Error code: {code}",
                "exit_code": 1,
                "category": "general"
            })
    elif isinstance(error_section, dict):
        # Enhanced format with metadata
        for i, (code, metadata) in enumerate(error_section.items()):
            if isinstance(metadata, dict):
                error_codes.append({
                    "code": code,
                    "number": i + 1,
                    "description": metadata.get("description", f"Error code: {code}"),
                    "exit_code": metadata.get("exit_code", 1),
                    "category": metadata.get("category", "general")
                })
            else:
                error_codes.append({
                    "code": code,
                    "number": i + 1,
                    "description": f"Error code: {code}",
                    "exit_code": 1,
                    "category": "general"
                })
    
    return error_codes


def infer_node_capabilities(contract: dict) -> List[str]:
    """Infer node capabilities from contract"""
    capabilities = ["SUPPORTS_SCHEMA_VALIDATION"]  # All nodes support schema validation
    
    # Check for event bus support
    input_props = contract.get("input_state", {}).get("properties", {})
    output_props = contract.get("output_state", {}).get("properties", {})
    
    if any(field in input_props for field in ["event_id", "correlation_id"]) or \
       any(field in output_props for field in ["event_id", "correlation_id"]):
        capabilities.append("SUPPORTS_EVENT_BUS")
    
    # Check for CLI support
    if extract_cli_interface(contract):
        capabilities.append("SUPPORTS_CLI")
    
    # Check for validation capabilities
    if contract.get("error_codes"):
        capabilities.append("SUPPORTS_ERROR_HANDLING")
    
    # Check for external dependencies
    input_props = contract.get("input_state", {}).get("properties", {})
    if "external_dependency" in input_props:
        capabilities.append("SUPPORTS_EXTERNAL_DEPENDENCIES")
    
    return capabilities


def tool_generate_introspection(contract_path: Path, output_path: Path):
    """
    Generate enhanced introspection.py from contract.yaml using NodeIntrospectionResponse model.
    Eliminates all TODOs and provides complete metadata extraction.
    
    Args:
        contract_path: Path to the contract.yaml file
        output_path: Path to write the generated introspection.py file
    """
    # Load contract
    with open(contract_path, "r") as f:
        contract = yaml.safe_load(f)
    
    version_dir = output_path.parent
    node_dir = version_dir.parent
    introspection_path = version_dir / "introspection.py"
    
    # Load pyproject.toml for dependencies
    pyproject = toml.load("pyproject.toml")
    python_version = pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {}).get("python", ">=3.11,<3.12")
    runtime_deps = [k for k in pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {}).keys() if k != "python"]
    
    # Load state.py for model class names
    state_path = version_dir / "models" / "state.py"
    with open(state_path, "r") as f:
        state_code = f.read()
    
    input_model_match = re.search(r'class (\w+InputState)\(', state_code)
    output_model_match = re.search(r'class (\w+OutputState)\(', state_code)
    input_model = input_model_match.group(1) if input_model_match else "InputState"
    output_model = output_model_match.group(1) if output_model_match else "OutputState"
    
    # Extract enhanced metadata
    input_fields = extract_state_fields(contract.get("input_state", {}))
    output_fields = extract_state_fields(contract.get("output_state", {}))
    cli_interface = extract_cli_interface(contract)
    error_codes = extract_error_codes_with_metadata(contract)
    capabilities = infer_node_capabilities(contract)
    
    # Load error_codes.py for additional error codes
    error_codes_path = version_dir / "error_codes.py"
    if error_codes_path.exists() and not error_codes:
        with open(error_codes_path, "r") as f:
            for line in f:
                m = re.match(r'\s+(\w+) = ', line)
                if m:
                    error_codes.append({
                        "code": m.group(1),
                        "number": len(error_codes) + 1,
                        "description": f"Error code: {m.group(1)}",
                        "exit_code": 1,
                        "category": "general"
                    })
    
    # Generate enhanced introspection code
    header = (
        "# AUTO-GENERATED FILE. DO NOT EDIT.\n"
        "# Generated from contract.yaml with complete metadata extraction\n"
        "# To regenerate: run the node_manager codegen orchestrator.\n"
    )
    
    # Format fields for code generation
    input_fields_code = "[\n" + ",\n".join([
        f'                StateFieldModel(name="{field["name"]}", type="{field["type"]}", '
        f'description="{field["description"]}", required={field["required"]})'
        for field in input_fields
    ]) + "\n            ]" if input_fields else "[]"
    
    output_fields_code = "[\n" + ",\n".join([
        f'                StateFieldModel(name="{field["name"]}", type="{field["type"]}", '
        f'description="{field["description"]}", required={field["required"]})'
        for field in output_fields
    ]) + "\n            ]" if output_fields else "[]"
    
    # Format CLI interface
    cli_interface_code = "None"
    if cli_interface:
        cli_interface_code = f'''{{
            "command_name": "{cli_interface["command_name"]}",
            "description": "{cli_interface["description"]}",
            "parameters": {cli_interface["parameters"]},
            "examples": {cli_interface["examples"]}
        }}'''
    
    # Format error codes
    error_codes_code = "None"
    if error_codes:
        error_codes_list = ",\n".join([
            f'            ErrorCodeModel(code="{ec["code"]}", number={ec["number"]}, '
            f'description="{ec["description"]}", exit_code={ec["exit_code"]}, category="{ec["category"]}")'
            for ec in error_codes
        ])
        error_codes_code = f'''ErrorCodesModel(
            component="{contract.get('node_name', '')}",
            codes=[
{error_codes_list}
            ],
            total_codes={len(error_codes)},
        )'''
    
    # Format capabilities
    capabilities_code = ", ".join([f"NodeCapabilityEnum.{cap}" for cap in capabilities])
    
    code = f'''{header}
from omnibase.model.model_node_introspection import NodeIntrospectionResponse, NodeMetadataModel, ContractModel, StateModelsModel, StateModelModel, StateFieldModel, ErrorCodesModel, ErrorCodeModel, DependenciesModel, NodeCapabilityEnum

def get_node_introspection_response() -> NodeIntrospectionResponse:
    return NodeIntrospectionResponse(
        node_metadata=NodeMetadataModel(
            name="{contract.get('node_name', '')}",
            version="{contract.get('node_version', contract.get('contract_version', ''))}",
            description="{contract.get('contract_description', '')}",
            author="OmniNode Team",
            schema_version="{contract.get('contract_version', '')}",
        ),
        contract=ContractModel(
            input_state_schema="input_state",
            output_state_schema="output_state",
            cli_interface={cli_interface_code},
            protocol_version="1.0.0",
        ),
        state_models=StateModelsModel(
            input=StateModelModel(
                class_name="{input_model}",
                schema_version="{contract.get('contract_version', '')}",
                fields={input_fields_code},
                schema_file="models/state.py",
            ),
            output=StateModelModel(
                class_name="{output_model}",
                schema_version="{contract.get('contract_version', '')}",
                fields={output_fields_code},
                schema_file="models/state.py",
            ),
        ),
        error_codes={error_codes_code},
        dependencies=DependenciesModel(
            runtime={runtime_deps},
            optional=[],
            python_version="{python_version}",
            external_tools=[],
        ),
        capabilities=[{capabilities_code}],
        introspection_version="1.0.0",
    )
'''
    
    with open(introspection_path, "w") as f:
        f.write(code)
    
    emit_log_event_sync(
        LogLevelEnum.INFO,
        f"Generated enhanced introspection.py at {introspection_path} with {len(input_fields)} input fields, {len(output_fields)} output fields, {len(error_codes)} error codes, and {len(capabilities)} capabilities",
        context=make_log_context(node_id="introspection_generator"),
    ) 