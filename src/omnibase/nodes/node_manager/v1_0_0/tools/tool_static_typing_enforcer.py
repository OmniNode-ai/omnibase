import ast
import os
import sys
from pathlib import Path
from typing import Set, List, Tuple
import yaml
import typer

FORBIDDEN_PRIMITIVES = {"str", "dict", "list", "typing.Any", "Any"}
ALLOWED_PRIMITIVES = {"Path", "bytes", "int", "float", "bool"}  # Extend as needed

# Directories to scan
PROTOCOLS_DIR = Path(__file__).parent.parent / "protocols"
TOOLS_DIR = Path(__file__).parent / "tools"
MODELS_DIR = Path(__file__).parent.parent / "models"

WHITELISTED_STRING_FIELDS = {"event_id", "correlation_id", "node_name", "timestamp", "output_directory", "input_field", "message", "status"}
WHITELISTED_STRING_FORMATS = {"date-time", "uuid"}
WHITELISTED_INTEGER_FIELDS = {"total_schemas", "major", "minor", "patch"}

CONTRACT_PATH = Path(__file__).parent.parent / "contract.yaml"

def find_forbidden_types_in_signature(node: ast.FunctionDef) -> List[Tuple[str, str]]:
    """Return list of (arg_name, type_str) for forbidden types in function signature."""
    violations = []
    for arg in node.args.args:
        if arg.annotation:
            type_str = ast.unparse(arg.annotation)
            if type_str in FORBIDDEN_PRIMITIVES:
                violations.append((arg.arg, type_str))
    if node.returns:
        ret_type = ast.unparse(node.returns)
        if ret_type in FORBIDDEN_PRIMITIVES:
            violations.append(("return", ret_type))
    return violations


def scan_file_for_forbidden_types(filepath: Path) -> List[str]:
    """Scan a Python file for forbidden primitive types in function signatures."""
    with open(filepath, "r") as f:
        tree = ast.parse(f.read(), filename=str(filepath))
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            vios = find_forbidden_types_in_signature(node)
            for arg, type_str in vios:
                violations.append(f"{filepath}: {node.name} -> {arg}: {type_str}")
    return violations


def scan_directory_for_forbidden_types(directory: Path) -> List[str]:
    violations = []
    for file in directory.glob("*.py"):
        violations.extend(scan_file_for_forbidden_types(file))
    return violations


def scan_pydantic_models(directory: Path, import_base: str) -> List[str]:
    """Scan Pydantic models for forbidden primitive field types."""
    violations = []
    sys.path.insert(0, str(directory.parent.parent))  # Ensure import path
    for file in directory.glob("*.py"):
        if file.name == "__init__.py":
            continue
        module_name = f"{import_base}.{file.stem}"
        try:
            mod = __import__(module_name, fromlist=[file.stem])
        except Exception:
            continue  # Skip files that can't be imported
        for name in dir(mod):
            obj = getattr(mod, name)
            try:
                from pydantic import BaseModel
                if isinstance(obj, type) and issubclass(obj, BaseModel):
                    for field in obj.__fields__.values():
                        type_name = str(field.annotation)
                        if any(prim in type_name for prim in FORBIDDEN_PRIMITIVES):
                            violations.append(f"{file}: {obj.__name__}.{field.name}: {type_name}")
            except Exception:
                continue
    return violations


def scan_contract_yaml(contract_path: Path) -> List[str]:
    violations = []
    if not contract_path.exists():
        return violations
    with open(contract_path, "r") as f:
        docs = list(yaml.safe_load_all(f))
    contract = docs[-1] if docs else {}
    # Check input_state and output_state
    for state_key in ("input_state", "output_state"):
        state = contract.get(state_key, {})
        if state.get("type") == "object":
            props = state.get("properties", {})
            for field, spec in props.items():
                t = spec.get("type")
                fmt = spec.get("format")
                if t == "string":
                    if field not in WHITELISTED_STRING_FIELDS and (not fmt or fmt not in WHITELISTED_STRING_FORMATS):
                        violations.append(f"{contract_path}: {state_key}.{field} is type 'string' (not whitelisted)")
                elif t == "object":
                    violations.append(f"{contract_path}: {state_key}.{field} is type 'object' (should be model)")
                elif t == "array":
                    violations.append(f"{contract_path}: {state_key}.{field} is type 'array' (should be model or enum list)")
                elif t == "integer":
                    if field not in WHITELISTED_INTEGER_FIELDS:
                        violations.append(f"{contract_path}: {state_key}.{field} is type 'integer' (not whitelisted)")
    # Check definitions
    defs = contract.get("definitions", {})
    for def_name, def_spec in defs.items():
        if def_spec.get("type") == "object":
            props = def_spec.get("properties", {})
            for field, spec in props.items():
                t = spec.get("type")
                if t == "string":
                    if field not in WHITELISTED_STRING_FIELDS:
                        violations.append(f"{contract_path}: definitions.{def_name}.{field} is type 'string' (not whitelisted)")
                elif t == "object":
                    violations.append(f"{contract_path}: definitions.{def_name}.{field} is type 'object' (should be model)")
                elif t == "array":
                    violations.append(f"{contract_path}: definitions.{def_name}.{field} is type 'array' (should be model or enum list)")
                elif t == "integer":
                    if field not in WHITELISTED_INTEGER_FIELDS:
                        violations.append(f"{contract_path}: definitions.{def_name}.{field} is type 'integer' (not whitelisted)")
    return violations


def run_static_typing_enforcer(node_path: Path) -> List[str]:
    """Run the static typing enforcer on the given node path."""
    protocols_dir = node_path / "v1_0_0" / "protocols"
    tools_dir = node_path / "v1_0_0" / "tools"
    models_dir = node_path / "v1_0_0" / "models"
    contract_path = node_path / "v1_0_0" / "contract.yaml"
    import_base = f"src.omnibase.nodes.{node_path.name}.v1_0_0.models"
    all_violations = []
    all_violations.extend(scan_directory_for_forbidden_types(protocols_dir))
    all_violations.extend(scan_directory_for_forbidden_types(tools_dir))
    all_violations.extend(scan_pydantic_models(models_dir, import_base))
    all_violations.extend(scan_contract_yaml(contract_path))
    return all_violations


app = typer.Typer()

@app.command()
def cli_static_typing_enforce(
    node_path: Path = typer.Option(..., '--node-path', help='Path to the node directory to check (e.g., src/omnibase/nodes/node_manager)'),
):
    """
    Run static typing enforcement on the specified node directory.
    """
    violations = run_static_typing_enforcer(node_path)
    if violations:
        for v in violations:
            typer.echo(f"[VIOLATION] {v}")
        raise typer.Exit(code=1)
    else:
        typer.echo("[Static Typing Enforcer] No violations found. All clear!")

if __name__ == "__main__":
    app() 