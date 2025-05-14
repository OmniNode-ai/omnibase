import ast
import re
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent.parent / "logging" / "model"
UUID_V4_REGEX = re.compile(
    r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
)
UUID_FIELDS = {"uuid", "parent_id"}


def check_uuid_type_and_default(tree):
    errors = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            if name in UUID_FIELDS:
                # Check type hint
                type_str = (
                    ast.unparse(node.annotation) if hasattr(ast, "unparse") else None
                )
                if type_str and "UUID" not in type_str:
                    errors.append(
                        f"Field '{name}' does not use UUID type (found: {type_str})"
                    )
                # Check default value (should be None or omitted for parent_id)
                if name == "parent_id" and node.value is not None:
                    val = (
                        ast.literal_eval(node.value)
                        if isinstance(node.value, ast.Constant)
                        else None
                    )
                    if val is not None and val != "None":
                        errors.append(
                            f"Field 'parent_id' default is not None (found: {val})"
                        )
    return errors


def main():
    any_errors = False
    for file in MODEL_DIR.glob("*.py"):
        if file.name == "__init__.py":
            continue
        with open(file, "r") as f:
            tree = ast.parse(f.read(), filename=str(file))
        errors = check_uuid_type_and_default(tree)
        if errors:
            any_errors = True
            print(f"\n[ERROR] {file.name}:")
            for err in errors:
                print(f"  - {err}")
    if not any_errors:
        print(
            "All log entry models use correct UUID type for uuid and parent_id fields."
        )


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()
