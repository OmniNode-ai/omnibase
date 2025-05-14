#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# schema_version: 1.0.0
# name: python_validate_container
# namespace: omninode.tools.python_validate_container
# meta_type: model
# version: 0.1.0
# author: OmniNode Team
# owner: jonah@omninode.ai
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-05-03T22:59:58+00:00
# last_modified_at: 2025-05-03T22:59:58+00:00
# entrypoint: python_validate_container.py
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolValidate']
# base_class: ['ProtocolValidate']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""validate_container.py
containers.foundation.src.foundation.script.validate.validate_container.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import fnmatch
from pathlib import Path
from typing import Dict, List

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_unified_result import UnifiedResultModel
from foundation.model.model_validation_issue_mixin import ValidationIssueMixin
from foundation.protocol.protocol_in_memory_validate import ProtocolInMemoryValidate

class ContainerValidator(ValidationIssueMixin, ProtocolValidate, ProtocolInMemoryValidate):
    """Validates container structure and configuration."""

    def __init__(self, config=None):
        self.config = config or {}
        self.errors = []
        self.warnings = []
        super().__init__()

    @classmethod
    def metadata(cls) -> "MetadataBlockModel":
        from foundation.model.model_metadata import MetadataBlockModel
        return MetadataBlockModel(
            metadata_version="0.1",
            name="container",
            namespace="omninode.tools.python_validate_container",
            version="1.0.0",
            entrypoint="python_validate_container.py",
            protocols_supported=["O.N.E. v0.1"],
            author="OmniNode Team",
            owner="jonah@omninode.ai",
            copyright="Copyright (c) 2025 OmniNode.ai",
            created_at="2025-05-03T22:59:58+00:00",
            last_modified_at="2025-05-03T22:59:58+00:00",
            protocol_version="0.1.0",
            description="Validates container structure and configuration.",
            tags=["container", "validator", "python"],
            dependencies=[],
            config={}
        )

    def get_name(self) -> str:
        """Get the validator name."""
        return "container"

    def validate(self, target: Path, config: dict = None) -> UnifiedResultModel:
        """
        Validate container structure and configuration and return UnifiedResultModel.
        Args:
            target: Path to container directory
            config: Optional config dict (overrides self.config)
        Returns:
            UnifiedResultModel: The result of the validation
        """
        self.errors = []
        self.warnings = []
        if config is not None:
            self.config = config
        is_valid = self._validate(target)
        return UnifiedResultModel(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            metadata={"target": str(target)},
        )

    def _validate(self, target: Path) -> bool:
        """Validate container structure and configuration.

        Args:
            target: Path to container directory

        Returns:
            bool: True if validation passed
        """
        if not target.is_dir():
            self.add_error(
                message=f"Target {target} is not a directory",
                file=str(target),
                type="error",
            )
            return False

        # Get rules from config
        rules = self.config.get("rules", {})
        required_files = rules.get("required_files", [])
        naming_pattern = rules.get("naming_pattern", "")
        max_dockerfile_size = rules.get("max_dockerfile_size", 1000)
        init_py_rules = rules.get("init_py_rules", {})

        # Initialize validation status
        is_valid = True

        # Validate required files
        is_valid &= self._validate_required_files(target, required_files)

        # Validate container name
        is_valid &= self._validate_container_name(target, naming_pattern)

        # Validate Dockerfile size
        is_valid &= self._validate_dockerfile_size(target, max_dockerfile_size)

        # Validate __init__.py files
        is_valid &= self._validate_init_py_files(target, init_py_rules)

        return is_valid

    def _validate_required_files(self, target: Path, required_files: List[str]) -> bool:
        """Validate that all required files exist."""
        is_valid = True
        for file in required_files:
            file_path = target / file
            if not file_path.exists():
                self.add_error(
                    message=f"Required file {file} not found",
                    file=str(target),
                    details={"file": file},
                    type="error",
                )
                is_valid = False
        return is_valid

    def _validate_container_name(self, target: Path, pattern: str) -> bool:
        """Validate container name matches pattern."""
        import re

        if not pattern:
            return True

        name = target.name
        if not re.match(pattern, name):
            self.add_error(
                message=f"Container name {name} does not match pattern {pattern}",
                file=str(target),
                details={"name": name, "pattern": pattern},
                type="error",
            )
            return False
        return True

    def _validate_dockerfile_size(self, target: Path, max_size: int) -> bool:
        """Validate Dockerfile size is within limits."""
        dockerfile = target / "Dockerfile"
        if not dockerfile.exists():
            return True  # Already checked in required files

        size = len(dockerfile.read_text().splitlines())
        if size > max_size:
            self.add_error(
                message=f"Dockerfile exceeds maximum size of {max_size} lines",
                file=str(dockerfile),
                details={"size": size, "max_size": max_size},
                type="error",
            )
            return False
        return True

    def _validate_init_py_files(self, target: Path, init_py_rules: Dict) -> bool:
        """Validate __init__.py files according to rules.

        Args:
            target: Path to container directory
            init_py_rules: Dictionary containing required_patterns and ignore_patterns

        Returns:
            bool: True if validation passed
        """
        is_valid = True
        required_patterns = init_py_rules.get("required_patterns", [])
        ignore_patterns = init_py_rules.get("ignore_patterns", [])

        # Get all Python files in the container
        python_files = list(target.rglob("*.py"))

        # Check each Python file's directory
        checked_dirs = set()
        for py_file in python_files:
            py_dir = py_file.parent
            if py_dir in checked_dirs:
                continue

            checked_dirs.add(py_dir)
            rel_path = str(py_dir.relative_to(target))

            # Skip if directory matches any ignore pattern
            if any(fnmatch.fnmatch(rel_path, pat) for pat in ignore_patterns):
                continue

            # Check if directory requires __init__.py
            requires_init = any(
                fnmatch.fnmatch(rel_path, pat) for pat in required_patterns
            )
            if requires_init and not (py_dir / "__init__.py").exists():
                self.add_error(
                    message="Missing __init__.py in required Python package directory",
                    file=str(py_dir),
                    details={"directory": rel_path},
                    type="error",
                )
                is_valid = False

        return is_valid

    def validate_content(self, content: str, config: dict = None, directory_name: str = None) -> UnifiedResultModel:
        """
        Validate the given container configuration from an in-memory YAML string describing the directory structure.
        Args:
            content: The YAML content describing the directory/files
            config: Optional configuration dictionary
            directory_name: Optional directory name to simulate for name pattern validation
        Returns:
            UnifiedResultModel: The result of the validation
        """
        import yaml
        from pathlib import Path
        import tempfile
        import os
        file_map = yaml.safe_load(content)
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdir = Path(tmpdirname)
            for fname, fcontent in (file_map or {}).items():
                (tmpdir / fname).write_text(fcontent if fcontent is not None else "")
            if directory_name:
                parent = tmpdir.parent
                new_dir = parent / directory_name
                os.rename(tmpdir, new_dir)
                tmpdir = new_dir
            return self.validate(tmpdir, config or self.config)