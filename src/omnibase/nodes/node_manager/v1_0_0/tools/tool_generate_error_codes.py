from pathlib import Path

def pascal_case(s: str) -> str:
    return "".join(word.capitalize() for word in s.replace('-', '_').split('_'))

def tool_generate_error_codes(contract_path: Path, output_path: Path):
    """
    Generate error_codes.py from contract.yaml if error_codes are defined (not a $ref).
    Args:
        contract_path: Path to the contract.yaml file
        output_path: Path to write the generated error_codes.py file
    """
    import yaml
    with open(contract_path, "r") as f:
        contract = yaml.safe_load(f)
    error_codes = contract.get("error_codes")
    if error_codes is None:
        # No error codes defined; do not generate file
        return
    if isinstance(error_codes, dict) and "$ref" in error_codes:
        # Reference to shared enum; do not generate file
        print(f"[INFO] error_codes is a $ref to shared enum: {error_codes['$ref']}. Skipping error_codes.py generation.")
        return
    if isinstance(error_codes, list):
        codes = error_codes
    elif isinstance(error_codes, dict):
        codes = list(error_codes.keys())
    else:
        print(f"[WARN] error_codes section is not a list or mapping; skipping error_codes.py generation.")
        return
    node_name = contract.get("node_name") or contract.get("contract_name") or "Node"
    enum_class = f"{pascal_case(node_name)}ErrorCode"
    header = f"""# AUTO-GENERATED FILE. DO NOT EDIT.\n# Generated from contract.yaml\n# To regenerate: run the node_manager codegen orchestrator.\n"""
    lines = [header, "from enum import Enum", "", f"class {enum_class}(Enum):"]
    for code in codes:
        lines.append(f"    {code} = '{code}'")
    lines.append("")
    output_file = output_path.parent.parent / "error_codes.py"
    with open(output_file, "w") as f:
        f.write("\n".join(lines))
    print(f"[INFO] Generated error_codes.py with {len(codes)} codes at {output_file}") 