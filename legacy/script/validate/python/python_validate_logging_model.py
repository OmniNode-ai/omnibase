import ast
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent.parent / "logging" / "model"
REQUIRED_FIELDS = {"uuid", "timestamp", "parent_id"}


def is_pydantic_model_or_abc(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = {
                b.id if isinstance(b, ast.Name) else getattr(b, "attr", None)
                for b in node.bases
            }
            if "BaseModel" in bases or "ABC" in bases or "Protocol" in bases:
                return True
    return False


def has_required_fields(tree):
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            found.add(node.target.id)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    found.add(t.id)
    return REQUIRED_FIELDS.issubset(found)


def validate_model_file(path):
    errors = []
    if not path.name.startswith("model_"):
        errors.append(f"File name does not start with 'model_': {path.name}")
    with open(path, "r") as f:
        tree = ast.parse(f.read(), filename=str(path))
    if not is_pydantic_model_or_abc(tree):
        errors.append(f"No Pydantic model or ABC/Protocol found in {path.name}")
    if not has_required_fields(tree):
        errors.append(
            f"Missing one or more required fields ({', '.join(REQUIRED_FIELDS)}) in {path.name}"
        )
    return errors


def main():
    any_errors = False
    for file in MODEL_DIR.glob("*.py"):
        if file.name == "__init__.py":
            continue
        errors = validate_model_file(file)
        if errors:
            any_errors = True
            print(f"\n[ERROR] {file.name}:")
            for err in errors:
                print(f"  - {err}")
    if not any_errors:
        print("All logging model files are compliant.")


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()
