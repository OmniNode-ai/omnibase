import ast
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent.parent / "logging" / "model"
REQUIRED_OPTIONAL_FIELDS = {
    "type_tags": "List[str]",
    "github_reference": "Optional[str]",
    "agent_name": "Optional[str]",
    "response_summary": "Optional[str]",
    "execution_context": "Optional[str]",
}


def check_fields(tree):
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            type_str = ast.unparse(node.annotation) if hasattr(ast, "unparse") else None
            found[name] = type_str
    errors = []
    for field, expected_type in REQUIRED_OPTIONAL_FIELDS.items():
        if field not in found:
            errors.append(f"Missing required field: {field}")
        elif expected_type not in (found[field] or ""):
            errors.append(
                f"Field '{field}' does not have expected type {expected_type} (found: {found[field]})"
            )
    return errors


def main():
    any_errors = False
    for file in MODEL_DIR.glob("*.py"):
        if file.name == "__init__.py":
            continue
        with open(file, "r") as f:
            tree = ast.parse(f.read(), filename=str(file))
        errors = check_fields(tree)
        if errors:
            any_errors = True
            print(f"\n[ERROR] {file.name}:")
            for err in errors:
                print(f"  - {err}")
    if not any_errors:
        print("All log entry models have required type_tags and optional fields.")


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()
