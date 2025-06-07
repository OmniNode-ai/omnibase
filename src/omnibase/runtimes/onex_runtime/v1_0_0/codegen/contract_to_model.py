"""
contract_to_model.py

Contract-driven model generator for ONEX nodes.

- Reads a contract.yaml file and generates canonical Pydantic models for input and output state.
- Intended for use by the runtime node, CLI tools, and developer workflows.
- Ensures all node models are always in sync with the contract (no drift).

Future: This logic will be integrated into the runtime node for dynamic model generation and validation.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict

import yaml

from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import (
    emit_log_event_sync,
    make_log_context,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.hash_utils import compute_canonical_hash

type_map = {
    "string": "str",
    "integer": "int",
    "boolean": "bool",
    "number": "float",
    # Extend as needed
}


def _enum_class(name: str, values: list) -> str:
    # Convert field name to PascalCase for class name
    class_name = (
        "".join(word.capitalize() for word in re.split(r"[_\-]", name)) + "Enum"
    )
    lines = [f"class {class_name}(str, Enum):"]
    for v in values:
        lines.append(f'    {v.lower()} = "{v}"')
    return "\n".join(lines), class_name


# Canonical OnexStatus values
ONEX_STATUS_VALUES = [
    "success",
    "warning",
    "error",
    "skipped",
    "fixed",
    "partial",
    "info",
    "unknown",
]


def pascal_case(s: str) -> str:
    return "".join(word.capitalize() for word in re.split(r"[_\-]", s))


def _field_line(
    name: str, field: dict, required: bool, enums: dict, status_enum_mode: str, custom_defs: dict = None
) -> str:
    # DEBUG: Print field processing info
    ref = field.get("$ref", None)
    print(f"[DEBUG][_field_line] name={name}, required={required}, $ref={ref}, field={field}")
    # Use canonical OnexStatus for status field if mode is 'onex'
    if name == "status" and status_enum_mode == "onex":
        py_type = "OnexStatus"
        import_onex_status = True
        import_onex_field = False
        import_semver = False
    elif "$ref" in field:
        ref = field["$ref"]
        if ref == "#/definitions/OnexFieldModel":
            py_type = "OnexFieldModel"
            import_onex_field = True
            import_semver = False
        elif ref == "#/definitions/SemVerModel":
            py_type = "SemVerModel"
            import_onex_field = False
            import_semver = True
            if not required:
                py_type = f"Optional[{py_type}]"
        elif ref.startswith("#/definitions/"):
            # Custom model reference
            model_name = ref.split("/")[-1]
            py_type = model_name
            import_onex_field = False
            import_semver = False
        else:
            py_type = "Any"  # fallback for unknown refs
            import_onex_field = False
            import_semver = False
        import_onex_status = False
    else:
        py_type = type_map.get(field.get("type", "string"), "str")
        import_onex_field = False
        import_onex_status = False
        import_semver = False
        enum = field.get("enum")
        if enum and not (name == "status" and status_enum_mode == "onex"):
            py_type = enums[name]  # Use generated Enum class name
        if not required:
            py_type = f"Optional[{py_type}]"
    desc = field.get("description", "")
    default = field.get("default")
    # For optional fields, do not set a default if not present in contract
    line = f"    {name}: {py_type}"
    if not required and default is None:
        line += " = None"
    elif default is not None:
        if isinstance(default, str):
            line += f' = "{default}"'
        else:
            line += f" = {repr(default)}"
    line += f"  # {desc}"
    if field.get("enum"):
        line += f"  # Allowed: {field['enum']}"
    # DEBUG: Print resulting line and type
    print(f"[DEBUG][_field_line] RESULT name={name}, py_type={py_type}, line={line}")
    return line, import_onex_field, import_onex_status, import_semver


def _model_block(
    class_name: str,
    schema: dict,
    required_fields: set,
    enums: dict,
    status_enum_mode: str,
):
    lines = [f"class {class_name}(BaseModel):"]
    props = schema.get("properties", {})
    import_onex_field = False
    import_onex_status = False
    import_semver = False
    needs_version_validator = False
    needs_event_id_validator = False
    needs_timestamp_validator = False
    for name, field in props.items():
        required = name in required_fields
        field_line, field_import, status_import, semver_import = _field_line(
            name, field, required, enums, status_enum_mode
        )
        lines.append(field_line)
        if field_import:
            import_onex_field = True
        if status_import:
            import_onex_status = True
        if semver_import:
            import_semver = True
        if name == "version":
            needs_version_validator = True
        if name == "event_id":
            needs_event_id_validator = True
        if name == "timestamp":
            needs_timestamp_validator = True
    if len(props) == 0:
        lines.append("    pass")
    if needs_version_validator:
        lines.append("")
        lines.append("    @field_validator(\"version\", mode=\"before\")")
        lines.append("    @classmethod")
        lines.append("    def parse_version(cls, v):")
        lines.append("        from omnibase.model.model_semver import SemVerModel")
        lines.append("        if isinstance(v, SemVerModel):")
        lines.append("            return v")
        lines.append("        if isinstance(v, str):")
        lines.append("            return SemVerModel.parse(v)")
        lines.append("        if isinstance(v, dict):")
        lines.append("            return SemVerModel(**v)")
        lines.append("        raise ValueError(\"version must be a string, dict, or SemVerModel\")")
    if needs_event_id_validator:
        lines.append("")
        lines.append("    @field_validator(\"event_id\")")
        lines.append("    @classmethod")
        lines.append("    def validate_event_id(cls, v):")
        lines.append("        import uuid")
        lines.append("        try:")
        lines.append("            uuid.UUID(str(v))")
        lines.append("            return str(v)")
        lines.append("        except Exception:")
        lines.append("            raise ValueError(\"event_id must be a valid UUID string\")")
    if needs_timestamp_validator:
        lines.append("")
        lines.append("    @field_validator(\"timestamp\")")
        lines.append("    @classmethod")
        lines.append("    def validate_timestamp(cls, v):")
        lines.append("        from datetime import datetime")
        lines.append("        try:")
        lines.append("            datetime.fromisoformat(v.replace('Z', '+00:00'))")
        lines.append("            return v")
        lines.append("        except Exception:")
        lines.append("            raise ValueError(\"timestamp must be a valid ISO8601 string\")")
    return "\n".join(lines), import_onex_field, import_onex_status, import_semver


def generate_error_codes(contract_path: Path, output_path: Path, contract: dict, contract_hash: str):
    """
    Generate error_codes.py from contract.yaml if error_codes are defined (not a $ref).
    Args:
        contract_path: Path to the contract.yaml file
        output_path: Path to write the generated error_codes.py file
        contract: Parsed contract dict
        contract_hash: Canonical hash of contract.yaml
    """
    error_codes = contract.get("error_codes")
    if error_codes is None:
        # No error codes defined; do not generate file
        return
    if isinstance(error_codes, dict) and "$ref" in error_codes:
        # Reference to shared enum; do not generate file
        print(f"[INFO] error_codes is a $ref to shared enum: {error_codes['$ref']}. Skipping error_codes.py generation.")
        return
    # Otherwise, generate error_codes.py
    # Accept both list and mapping (for future extensibility)
    if isinstance(error_codes, list):
        codes = error_codes
    elif isinstance(error_codes, dict):
        codes = list(error_codes.keys())
    else:
        print(f"[WARN] error_codes section is not a list or mapping; skipping error_codes.py generation.")
        return
    # Determine enum class name from node_name or contract_name
    node_name = contract.get("node_name") or contract.get("contract_name") or "Node"
    enum_class = f"{pascal_case(node_name)}ErrorCode"
    header = f"""# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
# contract_hash: {contract_hash}
# To regenerate: poetry run python src/omnibase/runtimes/onex_runtime/v1_0_0/codegen/contract_to_model.py --contract {contract_path} --output-dir {output_path.parent}
"""
    lines = [header, "from enum import Enum", "", f"class {enum_class}(Enum):"]
    for code in codes:
        lines.append(f"    {code} = '{code}'")
    lines.append("")
    # Always write error_codes.py to the node version directory (parent of output_path)
    output_file = output_path.parent.parent / "error_codes.py"
    with open(output_file, "w") as f:
        f.write("\n".join(lines))
    print(f"[INFO] Generated error_codes.py with {len(codes)} codes at {output_file}")


def generate_state_models(
    contract_path: Path, output_path: Path, force: bool = False, auto: bool = False
):
    """
    Generate Pydantic models for input/output state from a contract.yaml file.
    Args:
        contract_path: Path to the contract.yaml file
        output_path: Path to write the generated state.py file
    """
    emit_log_event_sync(
        LogLevelEnum.TRACE,
        f"Starting model generation from contract: {contract_path} to {output_path} (force={force}, auto={auto})",
        context=make_log_context(node_id="contract_to_model"),
    )
    with open(contract_path, "r") as f:
        contract_content = f.read()
    contract_hash = compute_canonical_hash(contract_content)
    contract = yaml.safe_load(contract_content)
    input_schema = contract.get("input_state", {})
    output_schema = contract.get("output_state", {})
    input_required = set(input_schema.get("required", []))
    output_required = set(output_schema.get("required", []))

    # DEBUG: Emit parsed input/output properties
    emit_log_event_sync(
        LogLevelEnum.DEBUG,
        f"Parsed input_state properties: {list(input_schema.get('properties', {}).keys())}",
        context=make_log_context(node_id="contract_to_model"),
    )
    emit_log_event_sync(
        LogLevelEnum.DEBUG,
        f"Parsed output_state properties: {list(output_schema.get('properties', {}).keys())}",
        context=make_log_context(node_id="contract_to_model"),
    )

    # Determine prefix from node_name or contract_name
    node_name = contract.get("node_name") or contract.get("contract_name") or ""
    prefix = pascal_case(node_name) if node_name else ""

    # Determine if status enum matches canonical OnexStatus
    status_enum_mode = "local"
    status_field = output_schema.get("properties", {}).get("status")
    if status_field and "enum" in status_field:
        contract_status_values = status_field["enum"]
        if sorted(contract_status_values) == sorted(ONEX_STATUS_VALUES):
            status_enum_mode = "onex"
        else:
            logging.warning(
                f"[DEBUG] Contract status enum does not match OnexStatus: {contract_status_values}"
            )
            status_enum_mode = "local"

    # Collect enums from both input and output
    enums = {}
    enum_defs = []
    for schema, _required in [
        (input_schema, input_required),
        (output_schema, output_required),
    ]:
        props = schema.get("properties", {})
        for name, field in props.items():
            if "enum" in field and not (
                name == "status" and status_enum_mode == "onex"
            ):
                enum_code, enum_class = _enum_class(name, field["enum"])
                if enum_class not in enums.values():
                    enum_defs.append(enum_code)
                enums[name] = enum_class

    # Collect custom definitions
    custom_defs = contract.get("definitions", {})

    # Generate custom model classes for all custom definitions
    custom_model_blocks = []
    for def_name, def_schema in custom_defs.items():
        if def_name in ("OnexFieldModel", "SemVerModel"):
            continue  # handled by imports
        # Only handle object types
        if def_schema.get("type") == "object":
            lines = [f"class {def_name}(BaseModel):"]
            props = def_schema.get("properties", {})
            required_fields = set(def_schema.get("required", []))
            if not props:
                lines.append("    pass")
            else:
                for pname, pfield in props.items():
                    prequired = pname in required_fields
                    ptype = type_map.get(pfield.get("type", "string"), "str")
                    if not prequired:
                        ptype = f"Optional[{ptype}]"
                    lines.append(f"    {pname}: {ptype}")
            custom_model_blocks.append("\n".join(lines))

    # Compose header with command reference
    header = (
        "# AUTO-GENERATED FILE. DO NOT EDIT.\n"
        "# Generated from contract.yaml\n"
        f"# contract_hash: {contract_hash}\n"
        f"# To regenerate: poetry run onex run schema_generator_node --args='[\"{contract_path}\", \"{output_path}\"]'\n"
        "from typing import Optional\nfrom pydantic import BaseModel, field_validator\n"
    )
    import_lines = []
    if enum_defs:
        import_lines.append("from enum import Enum")
        import_lines.append("\n".join(enum_defs))
    # Generate models and check if OnexFieldModel, OnexStatus, or SemVerModel is needed
    input_model, input_import, input_status_import, input_semver_import = _model_block(
        f"{prefix}InputState", input_schema, input_required, enums, status_enum_mode
    )
    output_model, output_import, output_status_import, output_semver_import = (
        _model_block(
            f"{prefix}OutputState",
            output_schema,
            output_required,
            enums,
            status_enum_mode,
        )
    )
    if input_import or output_import:
        import_lines.append(
            "from omnibase.model.model_output_field import OnexFieldModel"
        )
    if input_status_import or output_status_import:
        import_lines.append("from omnibase.enums.onex_status import OnexStatus")
    if input_semver_import or output_semver_import:
        import_lines.append("from omnibase.model.model_semver import SemVerModel")
    if import_lines:
        header += "\n".join(import_lines) + "\n"
    code = f"{header}\n\n" + ("\n\n".join(custom_model_blocks) + "\n\n" if custom_model_blocks else "") + f"{input_model}\n\n{output_model}\n"
    with open(output_path, "w") as f:
        f.write(code)
    emit_log_event_sync(
        LogLevelEnum.TRACE,
        f"Model generation complete: {output_path}",
        context=make_log_context(node_id="contract_to_model"),
    )

    # After generating state.py, generate error_codes.py if needed
    generate_error_codes(contract_path, output_path, contract, contract_hash)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 3:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            "Usage: python contract_to_model.py <contract.yaml> <output_state.py> [--force]",
            context=make_log_context(node_id="contract_to_model"),
        )
        sys.exit(1)
    contract_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    force = "--force" in sys.argv
    if not contract_path.exists():
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Contract file not found: {contract_path}",
            context=make_log_context(node_id="contract_to_model"),
        )
        sys.exit(1)
    if output_path.exists() and not force:
        # Check if contract has changed since last generation
        with open(contract_path, 'r') as f:
            contract_content = f.read()
        contract_hash = compute_canonical_hash(contract_content)
        # Try to find the hash in the output file (look for a comment line)
        output_hash = None
        with open(output_path, 'r') as f:
            for line in f:
                if line.strip().startswith('# contract_hash:'):
                    output_hash = line.strip().split(':', 1)[1].strip()
                    break
        if output_hash and output_hash != contract_hash:
            emit_log_event_sync(
                LogLevelEnum.WARNING,
                f"Contract has changed since last model generation. Use --force to regenerate {output_path}.",
                context=make_log_context(node_id="contract_to_model"),
            )
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Output file {output_path} exists. Use --force to overwrite.",
            context=make_log_context(node_id="contract_to_model"),
        )
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"Model generation skipped: {output_path} already exists and --force not set.",
            context=make_log_context(node_id="contract_to_model"),
        )
        sys.exit(1)
    emit_log_event_sync(
        LogLevelEnum.TRACE,
        f"Generating models from {contract_path} to {output_path} (force={force})",
        context=make_log_context(node_id="contract_to_model"),
    )
    try:
        generate_state_models(contract_path, output_path, force=force, auto=False)
        emit_log_event_sync(
            LogLevelEnum.TRACE,
            f"Model generation complete: {output_path}",
            context=make_log_context(node_id="contract_to_model"),
        )
    except Exception as e:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Exception during model generation: {e}",
            context=make_log_context(node_id="contract_to_model"),
        )
        sys.exit(1)
