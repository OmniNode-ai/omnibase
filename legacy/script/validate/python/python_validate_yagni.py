#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_yagni
# namespace: omninode.tools.validate_yagni
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:59+00:00
# last_modified_at: 2025-04-27T18:12:59+00:00
# entrypoint: validate_yagni.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_yagni.py
containers.foundation.src.foundation.script.validate.validate_yagni.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from foundation.protocol.protocol_tool import ProtocolTool


class YAGNIValidatorConfig(ValidatorConfig):
    version: str = "v1"
    exclude_dirs: List[str] = []
    flag_unused_functions: bool = True
    flag_unused_classes: bool = True
    flag_unused_imports: bool = True
    flag_speculative: bool = (
        True  # e.g., classes/functions with 'future', 'maybe', 'potential' in docstring/name
    )


class YAGNIValidator(ProtocolValidate, ProtocolTool):
    """Flags dead/unused/speculative code and over-engineered abstractions. Implements ProtocolTool."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = YAGNIValidatorConfig(**(config or {}))

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="yagni",
            group="quality",
            description="Flags dead/unused/speculative code and over-engineered abstractions.",
            version="v1",
        )

    def get_name(self) -> str:
        return "yagni"

    def validate(
        self, target: Path, config: Optional[YAGNIValidatorConfig] = None
    ) -> ValidationResult:
        cfg = config or self.config
        self.errors.clear()
        self.warnings.clear()
        is_valid = True
        python_files = [
            f
            for f in target.rglob("*.py")
            if not any(ex in f.parts for ex in cfg.exclude_dirs)
        ]
        for file in python_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content, filename=str(file))
                defined_funcs = set()
                called_funcs = set()
                defined_classes = set()
                instantiated_classes = set()
                imported_names = set()
                used_names = set()
                # Collect definitions and usage
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        defined_funcs.add(node.name)
                        # Speculative: check for 'future', 'maybe', 'potential' in name or docstring
                        if cfg.flag_speculative:
                            doc = ast.get_docstring(node) or ""
                            if any(
                                word in node.name.lower() or word in doc.lower()
                                for word in ("future", "maybe", "potential")
                            ):
                                is_valid = False
                                msg = f"Function '{node.name}' appears speculative (name/docstring contains 'future', 'maybe', or 'potential')"
                                self.errors.append(
                                    ValidationIssue(
                                        message=msg,
                                        file=str(file),
                                        line=getattr(node, "lineno", None),
                                    )
                                )
                    if isinstance(node, ast.ClassDef):
                        defined_classes.add(node.name)
                        if cfg.flag_speculative:
                            doc = ast.get_docstring(node) or ""
                            if any(
                                word in node.name.lower() or word in doc.lower()
                                for word in ("future", "maybe", "potential")
                            ):
                                is_valid = False
                                msg = f"Class '{node.name}' appears speculative (name/docstring contains 'future', 'maybe', or 'potential')"
                                self.errors.append(
                                    ValidationIssue(
                                        message=msg,
                                        file=str(file),
                                        line=getattr(node, "lineno", None),
                                    )
                                )
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            called_funcs.add(node.func.id)
                        elif isinstance(node.func, ast.Attribute):
                            called_funcs.add(node.func.attr)
                        if isinstance(node.func, ast.Name):
                            instantiated_classes.add(node.func.id)
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_names.add(alias.asname or alias.name)
                    if isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            imported_names.add(alias.asname or alias.name)
                    if isinstance(node, ast.Name):
                        used_names.add(node.id)
                # Unused functions
                if cfg.flag_unused_functions:
                    unused_funcs = defined_funcs - called_funcs - {"main"}
                    for func in unused_funcs:
                        is_valid = False
                        msg = f"Function '{func}' is defined but never called."
                        self.errors.append(ValidationIssue(message=msg, file=str(file)))
                # Unused classes
                if cfg.flag_unused_classes:
                    unused_classes = defined_classes - instantiated_classes
                    for cls in unused_classes:
                        is_valid = False
                        msg = f"Class '{cls}' is defined but never instantiated."
                        self.errors.append(ValidationIssue(message=msg, file=str(file)))
                # Unused imports
                if cfg.flag_unused_imports:
                    unused_imports = imported_names - used_names
                    for imp in unused_imports:
                        is_valid = False
                        msg = f"Import '{imp}' is never used."
                        self.errors.append(ValidationIssue(message=msg, file=str(file)))
            except Exception as e:
                self.warnings.append(
                    ValidationIssue(
                        message=f"Could not parse {file}: {e}", file=str(file)
                    )
                )
        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            version=cfg.version,
        )

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for YAGNIValidator."
        )

    def add_arguments(self) -> None:
        """Add CLI arguments to the parser (if used as a CLI tool)."""
        pass

    def run(self, dry_run: bool = False) -> ValidationResult:
        """Run the validator, supporting dry-run mode."""
        logger = logging.getLogger(__name__)
        if dry_run:
            logger.info("[DRY RUN] YAGNIValidator would validate for YAGNI violations.")
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        logger.info("Running YAGNIValidator.")
        # Example: validate current directory
        return self.validate(target=".")

    def execute(self) -> ValidationResult:
        """Standard entry point for execution."""
        return self.run(dry_run=False)
