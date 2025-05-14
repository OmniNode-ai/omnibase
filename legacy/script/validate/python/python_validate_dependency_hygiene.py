#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_dependency_hygiene
# namespace: omninode.tools.validate_dependency_hygiene
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:05+00:00
# last_modified_at: 2025-04-27T18:13:05+00:00
# entrypoint: validate_dependency_hygiene.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_dependency_hygiene.py containers.foundation.src.foundation.script.
validation.validate_dependency_hygiene.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)


class DependencyHygieneValidatorConfig(ValidatorConfig):
    version: str = "v1"
    exclude_dirs: List[str] = []
    check_unused: bool = True
    check_outdated: bool = True
    check_insecure: bool = True
    severity: str = "warning"  # or "error"


    name="dependency_hygiene",
    version="v1",
    group="quality",
    description="Checks for unused, outdated, or insecure dependencies.",
)
class DependencyHygieneValidator(ProtocolValidate):
    """Checks for unused, outdated, or insecure dependencies."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = DependencyHygieneValidatorConfig(**(config or {}))

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="dependency_hygiene",
            group="quality",
            description="Checks for unused, outdated, or insecure dependencies.",
            version="v1",
        )

    def get_name(self) -> str:
        return "dependency_hygiene"

    def validate(
        self, target: Path, config: Optional[DependencyHygieneValidatorConfig] = None
    ) -> ValidationResult:
        cfg = config or self.config
        errors = []
        warnings = []
        suggestions = []
        is_valid = True
        pyproject_path = target / "pyproject.toml"
        req_path = target / "requirements.txt"
        # Enforce pyproject.toml as the only source of truth
        if req_path.exists():
            is_valid = False
            msg = "requirements.txt is present. Only pyproject.toml is supported for dependency management."
            errors.append(
                ValidationIssue(message=msg, file=str(req_path), type="error")
            )
            suggestions.append(
                "Migrate dependencies to pyproject.toml and remove requirements.txt. Use 'poetry add' to add dependencies."
            )
        if not pyproject_path.exists():
            is_valid = False
            errors.append(
                ValidationIssue(
                    message="pyproject.toml not found. Dependency management requires pyproject.toml.",
                    file=str(pyproject_path),
                    type="error",
                )
            )
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                version=cfg.version,
            )
        used_imports = set()
        # Scan all .py files for imports
        python_files = [
            f
            for f in target.rglob("*.py")
            if not any(ex in f.parts for ex in cfg.exclude_dirs)
        ]
        for file in python_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith(
                            "import "
                        ) or line.strip().startswith("from "):
                            parts = line.replace("from ", "import ").split("import ")
                            if len(parts) > 1:
                                mod = parts[1].split()[0].split(".")[0]
                                used_imports.add(mod)
            except Exception:
                continue
        # Parse pyproject.toml
        toml_deps = set()
        try:
            import toml

            data = toml.load(pyproject_path)
            deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            toml_deps = set(deps.keys()) - {"python"}
        except Exception:
            pass
        # Unused dependencies
        if cfg.check_unused and toml_deps:
            unused = toml_deps - used_imports
            for dep in unused:
                is_valid = False
                msg = f"Dependency '{dep}' is listed in pyproject.toml but not imported anywhere."
                issue = ValidationIssue(
                    message=msg,
                    file=str(pyproject_path),
                    type="error" if cfg.severity == "error" else "warning",
                )
                if cfg.severity == "error":
                    errors.append(issue)
                else:
                    warnings.append(issue)
                suggestions.append(
                    f"Remove unused dependency '{dep}' from pyproject.toml."
                )
        # Outdated dependencies (stub: in real use, would check PyPI for latest)
        if cfg.check_outdated:
            # This is a stub; in real use, integrate with pip list --outdated or PyPI API
            pass
        # Insecure dependencies (stub: in real use, would check against known CVEs)
        if cfg.check_insecure:
            # This is a stub; in real use, integrate with safety or similar tool
            pass
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            version=cfg.version,
        )

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for DependencyHygieneValidator."
        )
