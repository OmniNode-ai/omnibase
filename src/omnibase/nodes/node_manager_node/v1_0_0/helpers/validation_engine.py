"""
Validation engine for NodeGeneratorNode.

Handles validation of generated nodes to ensure they comply with ONEX standards
and have all required files and structure.
"""

from pathlib import Path
from typing import Any, Dict, List

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum


class ValidationEngine:
    """
    Engine for validating generated nodes against ONEX standards.

    Checks for required files, proper structure, and compliance with
    ONEX node conventions.
    """

    def __init__(self):
        """Initialize the validation engine."""
        self.required_files = [
            "node.py",
            "models/state.py",
            "models/__init__.py",
            "__init__.py",
            "node.onex.yaml",
            "contract.yaml",
            ".onexignore",
            "README.md",
            "CHANGELOG.md",
            "pytest.ini",
        ]
        self.required_directories = ["models", "helpers", "node_tests"]

    def validate_generated_node(
        self, node_path: Path, node_name: str
    ) -> Dict[str, Any]:
        """
        Validate a generated node for compliance with ONEX standards.

        Args:
            node_path: Path to the generated node directory
            node_name: Name of the generated node

        Returns:
            Dictionary containing validation results
        """
        emit_log_event(
            LogLevelEnum.INFO,
            f"Validating generated node: {node_name}",
            context={"node_path": str(node_path)},
            event_bus=self._event_bus,
        )
        errors = []
        warnings = []
        checked_files = []
        missing_files = []
        if not node_path.exists():
            errors.append(f"Node directory does not exist: {node_path}")
            return {
                "is_valid": False,
                "errors": errors,
                "warnings": warnings,
                "checked_files": checked_files,
                "missing_files": missing_files,
            }
        for required_file in self.required_files:
            file_path = node_path / "v1_0_0" / required_file
            if file_path.exists():
                checked_files.append(str(file_path))
                self._validate_file_content(file_path, node_name, warnings)
            else:
                missing_files.append(str(file_path))
                errors.append(f"Missing required file: {required_file}")
        for required_dir in self.required_directories:
            dir_path = node_path / "v1_0_0" / required_dir
            if not dir_path.exists():
                errors.append(f"Missing required directory: {required_dir}")
        if not node_path.name.endswith("_node"):
            warnings.append(f"Node directory should end with '_node': {node_path.name}")
        version_dir = node_path / "v1_0_0"
        if not version_dir.exists():
            errors.append("Missing v1_0_0 version directory")
        self._validate_node_manifest(node_path, node_name, errors, warnings)
        self._validate_contract_file(node_path, node_name, errors, warnings)
        self._validate_state_models(node_path, node_name, errors, warnings)
        is_valid = len(errors) == 0
        emit_log_event(
            LogLevelEnum.INFO,
            f"Validation complete: {'PASSED' if is_valid else 'FAILED'}",
            context={
                "errors": len(errors),
                "warnings": len(warnings),
                "checked_files": len(checked_files),
            },
            event_bus=self._event_bus,
        )
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "checked_files": checked_files,
            "missing_files": missing_files,
        }

    def _validate_file_content(
        self, file_path: Path, node_name: str, warnings: List[str]
    ) -> None:
        """
        Validate the content of a specific file.

        Args:
            file_path: Path to the file to validate
            node_name: Name of the node
            warnings: List to append warnings to
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            if "TEMPLATE" in content and file_path.suffix in [".py", ".yaml", ".md"]:
                warnings.append(
                    f"File contains unprocessed TEMPLATE placeholders: {file_path.name}"
                )
            if file_path.suffix == ".py":
                if (
                    f"{node_name}_node" not in content
                    and "node.py" not in file_path.name
                ):
                    warnings.append(
                        f"Python file may not reference node name properly: {file_path.name}"
                    )
        except Exception as e:
            warnings.append(f"Could not validate content of {file_path.name}: {e}")

    def _validate_node_manifest(
        self, node_path: Path, node_name: str, errors: List[str], warnings: List[str]
    ) -> None:
        """
        Validate the node.onex.yaml manifest file.

        Args:
            node_path: Path to the node directory
            node_name: Name of the node
            errors: List to append errors to
            warnings: List to append warnings to
        """
        manifest_path = node_path / "v1_0_0" / "node.onex.yaml"
        if not manifest_path.exists():
            return
        try:
            import yaml

            content = manifest_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            required_fields = [
                "name",
                "version",
                "description",
                "entrypoint",
                "namespace",
            ]
            for field in required_fields:
                if field not in data:
                    errors.append(f"node.onex.yaml missing required field: {field}")
            if "name" in data and data["name"] != f"{node_name}_node":
                warnings.append(
                    f"node.onex.yaml name field should be '{node_name}_node'"
                )
        except Exception as e:
            errors.append(f"Failed to parse node.onex.yaml: {e}")

    def _validate_contract_file(
        self, node_path: Path, node_name: str, errors: List[str], warnings: List[str]
    ) -> None:
        """
        Validate the contract.yaml file.

        Args:
            node_path: Path to the node directory
            node_name: Name of the node
            errors: List to append errors to
            warnings: List to append warnings to
        """
        contract_path = node_path / "v1_0_0" / "contract.yaml"
        if not contract_path.exists():
            return
        try:
            import yaml

            content = contract_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            required_fields = ["node_name", "input_state", "output_state"]
            for field in required_fields:
                if field not in data:
                    errors.append(f"contract.yaml missing required field: {field}")
            if "node_name" in data and data["node_name"] != f"{node_name}_node":
                warnings.append(f"contract.yaml node_name should be '{node_name}_node'")
        except Exception as e:
            errors.append(f"Failed to parse contract.yaml: {e}")

    def _validate_state_models(
        self, node_path: Path, node_name: str, errors: List[str], warnings: List[str]
    ) -> None:
        """
        Validate the state models file.

        Args:
            node_path: Path to the node directory
            node_name: Name of the node
            errors: List to append errors to
            warnings: List to append warnings to
        """
        state_path = node_path / "v1_0_0" / "models" / "state.py"
        if not state_path.exists():
            return
        try:
            content = state_path.read_text(encoding="utf-8")
            pascal_name = "".join(word.capitalize() for word in node_name.split("_"))
            expected_input_class = f"{pascal_name}InputState"
            expected_output_class = f"{pascal_name}OutputState"
            if expected_input_class not in content:
                warnings.append(f"state.py should contain class {expected_input_class}")
            if expected_output_class not in content:
                warnings.append(
                    f"state.py should contain class {expected_output_class}"
                )
            if "from pydantic import" not in content:
                errors.append("state.py should import from pydantic")
        except Exception as e:
            warnings.append(f"Could not validate state.py: {e}")
