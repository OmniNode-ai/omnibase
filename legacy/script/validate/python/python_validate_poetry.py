#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_poetry
# namespace: omninode.tools.validate_poetry
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:03+00:00
# last_modified_at: 2025-04-27T18:13:03+00:00
# entrypoint: validate_poetry.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_poetry.py
containers.foundation.src.foundation.script.validate.validate_poetry.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import re
from pathlib import Path
from typing import Dict, List

import toml
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorMetadata,
)

try:
    from foundation.protocol.protocol_validate import ProtocolValidate

except ImportError:
    from foundation.protocol.protocol_validate import ProtocolValidate


    name="poetry",
    version="v1",
    group="dependency",
    description="Validates poetry configuration and dependencies.",
)
class PoetryValidator(ProtocolValidate):
    """Validates poetry configuration and dependencies."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.warnings = []

    def get_name(self) -> str:
        """Get the validator name."""
        return "poetry"

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="poetry",
            group="dependency",
            description="Validates poetry configuration and dependencies.",
            version="v1",
        )

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for PoetryValidator."
        )

    def validate(self, target: Path) -> bool:
        """Validate poetry configuration.

        Args:
            target: Path to directory containing pyproject.toml

        Returns:
            bool: True if validation passed
        """
        pyproject_path = target / "pyproject.toml"
        if not pyproject_path.exists():
            self.errors.append(
                ValidationIssue(
                    message="pyproject.toml not found", file=str(target), type="error"
                )
            )
            return False

        try:
            config = toml.load(pyproject_path)
        except Exception as e:
            self.errors.append(
                ValidationIssue(
                    message=f"Failed to parse pyproject.toml: {e}",
                    file=str(pyproject_path),
                    type="error",
                )
            )
            return False

        # Get rules from config
        rules = self.config.get("rules", {})
        required_deps = rules.get("required_dependencies", [])
        forbidden_deps = rules.get("forbidden_dependencies", [])
        version_pattern = rules.get("version_pattern", "")

        # Initialize validation status
        is_valid = True

        # Validate dependencies
        is_valid &= self._validate_dependencies(config, required_deps, forbidden_deps)

        # Validate version format
        is_valid &= self._validate_version(config, version_pattern)

        return is_valid

    def _validate_dependencies(
        self, config: Dict, required: List[str], forbidden: List[str]
    ) -> bool:
        """Validate required and forbidden dependencies, and enforce foundation
        dependency."""
        is_valid = True
        # Get dependencies from pyproject.toml
        tool_poetry = config.get("tool", {}).get("poetry", {})
        dependencies = tool_poetry.get("dependencies", {})
        # Foundation enforcement
        if tool_poetry.get("name", "").lower() != "foundation":
            foundation_dep = dependencies.get("foundation")
            if not foundation_dep:
                self.errors.append(
                    ValidationIssue(
                        message="Required dependency 'foundation' not found in [tool.poetry.dependencies]",
                        details={"dependency": "foundation"},
                        type="error",
                    )
                )
                is_valid = False
            elif isinstance(foundation_dep, dict) and foundation_dep.get("path"):
                self.warnings.append(
                    ValidationIssue(
                        message="'foundation' dependency uses a local path. This is allowed for development, but should not be used in production/distributed builds.",
                        details={"dependency": foundation_dep},
                        type="warning",
                    )
                )
        # Check required dependencies
        for dep in required:
            if dep not in dependencies:
                self.errors.append(
                    ValidationIssue(
                        message=f"Required dependency {dep} not found",
                        details={"dependency": dep},
                        type="error",
                    )
                )
                is_valid = False
        # Check forbidden dependencies
        for dep in forbidden:
            if dep in dependencies:
                self.errors.append(
                    ValidationIssue(
                        message=f"Forbidden dependency {dep} found",
                        details={"dependency": dep},
                        type="error",
                    )
                )
                is_valid = False
        return is_valid

    def _validate_version(self, config: Dict, pattern: str) -> bool:
        """Validate version format."""
        if not pattern:
            return True

        tool_poetry = config.get("tool", {}).get("poetry", {})
        version = tool_poetry.get("version")

        if not version:
            self.errors.append(
                ValidationIssue(
                    message="Version not specified in pyproject.toml", type="error"
                )
            )
            return False

        if not re.match(pattern, version):
            self.errors.append(
                ValidationIssue(
                    message=f"Version {version} does not match pattern {pattern}",
                    details={"version": version, "pattern": pattern},
                    type="error",
                )
            )
            return False

        return True


def validate_poetry(path):
    """Module-level function for test compatibility."""
    validator = PoetryValidator(config={})
    is_valid = validator.validate(Path(path).parent)
    return ValidationResult(
        is_valid=is_valid,
        errors=getattr(validator, "errors", []),
        warnings=getattr(validator, "warnings", []),
        version="v1",
    )
