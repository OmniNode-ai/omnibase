#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_container_yaml
# namespace: omninode.tools.validate_container_yaml
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:57+00:00
# last_modified_at: 2025-04-27T18:12:57+00:00
# entrypoint: validate_container_yaml.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_container_yaml.py containers.foundation.src.foundation.script.vali
dation.validate_container_yaml.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from foundation.protocol.protocol_tool import ProtocolTool
from foundation.script.validate.common.common_validator_utils import get_changed_files
from .python_validate_container_metadata import (
    validate_container_yaml as _validate_container_yaml,
    validate_container_yaml_content,
)
from foundation.script.validate.validate_registry import ValidatorRegistry
from foundation.model.model_validation_issue_mixin import ValidationIssueMixin
from foundation.protocol.protocol_in_memory_validate import ProtocolInMemoryValidate

# Add the project root to sys.path for proper imports
sys.path.insert(0, str(Path(__file__).parents[2]))
try:
    from .python_validate_container_metadata import (
        validate_container_yaml as _validate_container_yaml,
    )
except ImportError:
    from container_metadata import validate_container_yaml as _validate_container_yaml

# Set up logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"), format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class ContainerYAMLValidatorConfig(ValidatorConfig):
    version: str = "1.0.0"
    # Add more config fields as needed


class ContainerYAMLValidator(ValidationIssueMixin, ProtocolValidate, ProtocolTool, ProtocolInMemoryValidate):
    """Validator for container.yaml files. Implements ProtocolTool and ProtocolInMemoryValidate."""

    def __init__(self, config=None, **dependencies):
        super().__init__()
        self.errors = []
        self.warnings = []
        self.failed_files = []
        self.config = ContainerYAMLValidatorConfig(**(config or {}))
        self.logger = dependencies.get("logger")

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="container_yaml",
            group="container",
            description="Validates container.yaml files for standardized containers.",
            version="1.0.0",
        )

    def validate(
        self, target: Path, config: Optional[ValidatorConfig] = None
    ) -> ValidationResult:
        """Validate a container.yaml file for standardized containers.

        Args:
            target: Path to container.yaml file
            config: Optional configuration
        Returns:
            ValidationResult: Result of the validation
        """
        self.errors.clear()
        self.warnings.clear()
        self.failed_files.clear()
        file_failed = False
        # Validate a single container.yaml file
        if not target.is_file():
            self.add_error(
                message=f"container.yaml not found: {target}",
                file=str(target),
                type="error",
            )
            file_failed = True
            return ValidationResult(
                is_valid=False, errors=self.errors, warnings=self.warnings
            )
        else:
            validation = _validate_container_yaml(str(target))
            if not validation.is_valid:
                for err in validation.errors:
                    if hasattr(err, "message"):
                        self.add_error(
                            message=err.message,
                            file=str(getattr(err, "file", str(target))),
                            line=getattr(err, "line", None),
                            details=getattr(err, "details", None),
                            type=getattr(err, "type", "error"),
                        )
                    else:
                        self.add_error(message=str(err), file=str(target), type="error")
                file_failed = True
            if validation.warnings:
                for warn in validation.warnings:
                    if hasattr(warn, "message"):
                        self.add_warning(
                            message=warn.message,
                            file=str(getattr(warn, "file", str(target))),
                            line=getattr(warn, "line", None),
                            details=getattr(warn, "details", None),
                            type=getattr(warn, "type", "warning"),
                        )
                    else:
                        self.add_warning(
                            message=str(warn), file=str(target), type="warning"
                        )
        if file_failed:
            self.add_failed_file(str(target))
        return ValidationResult(
            is_valid=not file_failed, errors=self.errors, warnings=self.warnings
        )

    def get_name(self) -> str:
        return "container_yaml"

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for ContainerYAMLValidator."
        )

    def add_arguments(self) -> None:
        """Add CLI arguments to the parser (if used as a CLI tool)."""
        pass

    def run(self, dry_run: bool = False) -> ValidationResult:
        """Run the validator, supporting dry-run mode."""
        if dry_run:
            if self.logger:
                self.logger.info(
                    "[DRY RUN] ContainerYAMLValidator would validate container.yaml files."
                )
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        if self.logger:
            self.logger.info("Running ContainerYAMLValidator.")
        # Example: validate current directory
        return self.validate(target=".")

    def execute(self) -> ValidationResult:
        """Standard entry point for execution."""
        return self.run(dry_run=False)

    def validate_content(self, content: str, config: dict = None):
        """
        Validate the given YAML content (in-memory string) and return a ValidationResult.
        Args:
            content: The YAML content to validate
            config: Optional configuration dictionary (currently unused)
        Returns:
            ValidationResult: The result of the validation
        """
        return validate_container_yaml_content(content)


try:
    # Attempt to use DI/registry pattern if available
    name = "container_yaml"
    version = "1.0.0"
    group = "container"
    description = "Validates container.yaml files for standardized containers."
    # If a decorator or registration function is available, use it here
    # Example (commented):
    # register_validator(name=name, version=version, group=group, description=description)(ContainerYAMLValidator)
    pass
except ImportError:
    from foundation.script.validate.python.python_validate_registry import validate_registry
    validate_registry.register(
        name="container_yaml",
        validator_cls=ContainerYAMLValidator,
        meta={
            "name": "container_yaml",
            "version": "1.0.0",
            "group": "container",
            "description": "Validates container.yaml files for standardized containers.",
        },
    )


def load_standardized_containers() -> List[Dict[str, Any]]:
    """Load the list of standardized containers from
    STANDARDIZED_CONTAINERS.json.

    Returns:
        List of standardized container dictionaries with name, path and other metadata
    """
    try:
        json_path = (
            Path(__file__).parents[2] / "containers" / "STANDARDIZED_CONTAINERS.json"
        )
        with open(json_path, "r") as f:
            data = json.load(f)
        return data.get("standardized_containers", [])
    except Exception as e:
        logger.error(f"Error loading standardized containers: {e}")
        return []


def validate_container_yaml_files(
    standardized_containers: List[Dict[str, Any]], changed_files: Set[str] = None
) -> bool:
    """Validate container.yaml files for standardized containers.

    Args:
        standardized_containers: List of standardized container dictionaries
        changed_files: Optional set of changed files to check

    Returns:
        True if all validations pass, False otherwise
    """
    all_valid = True
    validated_containers = set()

    for container in standardized_containers:
        container_path = container.get("path", "")
        container_name = container.get("name", "")

        if not container_path or not container_name:
            logger.warning(f"Invalid container definition: {container}")
            continue

        # Skip if we only want to check changed files and no files in this container were changed
        if changed_files is not None:
            container_files = {f for f in changed_files if f.startswith(container_path)}
            if not container_files:
                logger.info(f"No changes in {container_name}, skipping validation")
                continue

        # Avoid validating the same container twice
        if container_name in validated_containers:
            continue

        validated_containers.add(container_name)
        logger.info(f"Validating container.yaml for {container_name}")

        # Check if container.yaml exists
        yaml_path = Path(container_path) / "container.yaml"
        if not yaml_path.exists():
            logger.error(f"container.yaml not found for {container_name}")
            all_valid = False
            continue

        # Validate container.yaml
        result = validate_container_yaml(str(yaml_path))

        if not result.is_valid:
            logger.error(f"Validation failed for {container_name}:")
            for error in result.errors:
                logger.error(f"  - {error}")
            all_valid = False
        else:
            logger.info(f"Validation passed for {container_name}")
            if result.warnings:
                for warning in result.warnings:
                    logger.warning(f"  - {warning}")

    return all_valid


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate container.yaml files for standardized containers"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all standardized containers instead of just changed ones",
    )
    args = parser.parse_args()

    # Load standardized containers
    standardized_containers = load_standardized_containers()
    if not standardized_containers:
        logger.error("No standardized containers found")
        return 1

    logger.info(f"Found {len(standardized_containers)} standardized containers")

    # Get changed files if we're only checking changed containers
    changed_files = None if args.all else get_changed_files()

    # Validate container.yaml files
    if validate_container_yaml_files(standardized_containers, changed_files):
        logger.info("All container.yaml validations passed!")
        return 0
    else:
        logger.error("Some container.yaml validations failed")
        return 1


validate_container_yaml = _validate_container_yaml

if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    sys.exit(main())
