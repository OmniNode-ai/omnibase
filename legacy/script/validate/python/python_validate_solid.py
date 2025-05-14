#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_validate_solid"
# namespace: "omninode.tools.python_validate_solid"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:02+00:00"
# last_modified_at: "2025-05-05T12:44:02+00:00"
# entrypoint: "python_validate_solid.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolTool', 'ProtocolValidate', 'ValidatorConfig']
# base_class: ['ProtocolTool', 'ProtocolValidate', 'ValidatorConfig']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""validate_solid.py
containers.foundation.src.foundation.script.validate.validate_solid.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from foundation.protocol.protocol_tool import ProtocolTool
from foundation.script.validate.common.common_file_utils import find_files


class SOLIDCheckerConfig(ValidatorConfig):
    version: str = "v1"
    check_single_responsibility: bool = True
    check_open_closed: bool = True
    check_liskov_substitution: bool = True
    check_interface_segregation: bool = True
    check_dependency_inversion: bool = True
    suggestions: bool = True  # Show actionable suggestions
    examples: bool = True  # Show code examples in warnings


class SOLIDValidator(ProtocolValidate, ProtocolTool):
    """Validates adherence to SOLID principles. Implements ProtocolTool."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = SOLIDCheckerConfig(**(config or {}))

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="solid",
            group="quality",
            description="Validates adherence to SOLID principles in code.",
            version="v1",
        )

    def get_name(self) -> str:
        """Get the validator name."""
        return "solid"

    def validate(
        self, target: Path, config: Optional[SOLIDCheckerConfig] = None
    ) -> ValidationResult:
        """Validate SOLID principles.

        Args:
            target: Path to directory containing code

        Returns:
            ValidationResult: Result of the validation
        """
        cfg = config or self.config
        errors = []
        warnings = []
        suggestions = []
        is_valid = True
        scorecard = {}

        # Find Python files
        python_files = find_files(
            target,
            pattern="*.py",
            ignore_patterns=[
                "**/__pycache__/**",
                "**/tests/**",
                "**/test_*.py",
                "**/venv/**",
                "**/.venv/**",
                "**/.pytest_cache/**",
                "**/.mypy_cache/**",
            ],
        )

        if not python_files:
            errors.append("No Python files found")
            is_valid = False

        # Validate each file
        for file in python_files:
            file_score = {
                "SRP": True,
                "OCP": True,
                "LSP": True,
                "ISP": True,
                "DIP": True,
            }
            try:
                with open(file) as f:
                    content = f.read()
                if not content.strip():
                    errors.append(f"{file}: File is empty")
                    is_valid = False
                    continue
                tree = ast.parse(content)

                # Check Single Responsibility Principle
                if cfg.check_single_responsibility:
                    srp_valid = self._check_single_responsibility(
                        tree, file, errors, warnings
                    )
                    file_score["SRP"] = srp_valid
                    is_valid &= srp_valid

                # Check Open/Closed Principle
                if cfg.check_open_closed:
                    ocp_valid = self._check_open_closed(tree, file, errors, warnings)
                    file_score["OCP"] = ocp_valid
                    is_valid &= ocp_valid

                # Check Liskov Substitution Principle
                if cfg.check_liskov_substitution:
                    lsp_valid = self._check_liskov_substitution(
                        tree, file, errors, warnings
                    )
                    file_score["LSP"] = lsp_valid
                    is_valid &= lsp_valid

                # Check Interface Segregation Principle
                if cfg.check_interface_segregation:
                    isp_valid = self._check_interface_segregation(
                        tree, file, errors, warnings
                    )
                    file_score["ISP"] = isp_valid
                    is_valid &= isp_valid

                # Check Dependency Inversion Principle
                if cfg.check_dependency_inversion:
                    dip_valid = self._check_dependency_inversion(
                        tree, file, errors, warnings
                    )
                    file_score["DIP"] = dip_valid
                    is_valid &= dip_valid

            except Exception as e:
                errors.append(f"Failed to analyze {file.name}: {e}")
                is_valid = False
            scorecard[str(file)] = file_score

        # Add human-readable scorecard to suggestions
        if scorecard:
            summary_lines = ["SOLID Principle Scorecard:"]
            for file, scores in scorecard.items():
                passed = sum(1 for v in scores.values() if v)
                total = len(scores)
                summary_lines.append(
                    f"  {file}: {passed}/{total} principles passed | "
                    + ", ".join(f"{k}:{'✔' if v else '✘'}" for k, v in scores.items())
                )
            suggestions.append("\n".join(summary_lines))

        # Add JSON scorecard as a string to suggestions for CI/machine use
        suggestions.append(json.dumps({"scorecard": scorecard}))

        # Also add the raw scorecard to metadata for structured output
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            metadata={"scorecard": scorecard},
            version=cfg.version,
        )

    def _check_single_responsibility(
        self, tree: ast.AST, file: Path, errors: List[str], warnings: List[str]
    ) -> bool:
        """Check Single Responsibility Principle.

        Refined: Ignore dunder/private methods, only count public method categories.
        """
        is_valid = True
        cfg = self.config
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_types = defaultdict(int)
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        # Ignore dunder and private methods
                        if child.name.startswith("_"):
                            continue
                        prefix = child.name.split("_")[0]
                        method_types[prefix] += 1
                if len(method_types) > 3:
                    msg = f"{file}:{node.lineno}: Class '{node.name}' might violate Single Responsibility Principle (method categories: {dict(method_types)})"
                    if cfg.suggestions:
                        msg += f"\n  Suggestion: Consider splitting '{node.name}' into smaller classes, each with a single responsibility. Detected method categories: {list(method_types.keys())}."
                    if cfg.examples:
                        msg += (
                            "\n  Example:"
                            "\n  # Before:"
                            f"\n  class {node.name}:\n    def load_data(self): ..\n    def save_data(self): ..\n    def export_report(self): .."
                            "\n  # After:"
                            f"\n  class {node.name}Loader:\n    def load_data(self): ..\n  class {node.name}Saver:\n    def save_data(self): ..\n  class {node.name}Exporter:\n    def export_report(self): .."
                        )
                    warnings.append(msg)
                    is_valid = False
        return is_valid

    def _check_open_closed(
        self, tree: ast.AST, file: Path, errors: List[str], warnings: List[str]
    ) -> bool:
        """Check Open/Closed Principle."""
        is_valid = True
        cfg = self.config
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                type_checks = []
                for child in ast.walk(node):
                    if isinstance(child, ast.If):
                        if (
                            isinstance(child.test, ast.Call)
                            and isinstance(child.test.func, ast.Name)
                            and child.test.func.id == "isinstance"
                        ):
                            type_checks.append(child.lineno)
                if type_checks:
                    msg = f"{file}:{node.lineno}: Class '{node.name}' might violate Open/Closed Principle (type checking at lines {type_checks})"
                    if cfg.suggestions:
                        msg += "\n  Suggestion: Use polymorphism or abstract base classes to extend behavior instead of type checks."
                    if cfg.examples:
                        msg += (
                            "\n  Example:"
                            "\n  # Before:"
                            "\n  def process(self, x):\n    if isinstance(x, Foo): ..\n    elif isinstance(x, Bar): .."
                            "\n  # After:"
                            "\n  class Processor(ABC):\n    def process(self, x): ..\n  class FooProcessor(Processor):\n    def process(self, x): ..\n  class BarProcessor(Processor):\n    def process(self, x): .."
                        )
                    warnings.append(msg)
                    is_valid = False
        return is_valid

    def _check_liskov_substitution(
        self, tree: ast.AST, file: Path, errors: List[str], warnings: List[str]
    ) -> bool:
        """Check Liskov Substitution Principle."""
        is_valid = True
        cfg = self.config
        class_methods = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
                methods = {}
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        methods[child.name] = {
                            "args": len(child.args.args),
                            "defaults": len(child.args.defaults),
                        }
                class_methods[node.name] = {"bases": bases, "methods": methods}
        for class_name, info in class_methods.items():
            for base in info["bases"]:
                if base in class_methods:
                    base_methods = class_methods[base]["methods"]
                    for method, sig in base_methods.items():
                        if method in info["methods"] and info["methods"][method] != sig:
                            msg = f"{file}: Class '{class_name}' violates Liskov Substitution Principle for method '{method}'"
                            if cfg.suggestions:
                                msg += f"\n  Suggestion: Ensure '{class_name}.{method}' matches the signature of '{base}.{method}'."
                            if cfg.examples:
                                msg += (
                                    "\n  Example:"
                                    "\n  # Before:"
                                    f"\n  class {base}:\n    def foo(self, x): ..\n  class {class_name}({base}):\n    def foo(self, x, y): .."
                                    "\n  # After:"
                                    f"\n  class {class_name}({base}):\n    def foo(self, x): .."
                                )
                            errors.append(msg)
                            is_valid = False
        return is_valid

    def _check_interface_segregation(
        self, tree: ast.AST, file: Path, errors: List[str], warnings: List[str]
    ) -> bool:
        """Check Interface Segregation Principle.

        Refined: Only count public abstract methods, ignore dunder/private methods.
        """
        is_valid = True
        cfg = self.config
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                abstract_methods = []
                for child in node.body:
                    if (
                        isinstance(child, ast.FunctionDef)
                        and any(isinstance(d, ast.Pass) for d in child.body)
                        and not child.name.startswith("_")
                    ):
                        abstract_methods.append(child.name)
                if len(abstract_methods) > 5:
                    msg = f"{file}:{node.lineno}: Class '{node.name}' might violate Interface Segregation Principle (too many abstract methods: {abstract_methods})"
                    if cfg.suggestions:
                        msg += "\n  Suggestion: Split large interfaces into smaller, more focused ones. Clients should not be forced to depend on methods they do not use."
                    if cfg.examples:
                        msg += (
                            "\n  Example:"
                            "\n  # Before:"
                            f"\n  class {node.name}:\n    def a(self): ..\n    def b(self): ..\n    def c(self): ..\n    def d(self): ..\n    def e(self): ..\n    def f(self): .."
                            "\n  # After:"
                            f"\n  class {node.name}A:\n    def a(self): ..\n  class {node.name}B:\n    def b(self): .."
                        )
                    warnings.append(msg)
                    is_valid = False
        return is_valid

    def _check_dependency_inversion(
        self, tree: ast.AST, file: Path, errors: List[str], warnings: List[str]
    ) -> bool:
        """Check Dependency Inversion Principle."""
        is_valid = True
        cfg = self.config
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                concrete_deps = []
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        class_name = child.func.id
                        if class_name[0].isupper() and not class_name.endswith(
                            "Interface"
                        ):
                            concrete_deps.append(class_name)
                if concrete_deps:
                    msg = f"{file}:{node.lineno}: Class '{node.name}' might violate Dependency Inversion Principle (direct instantiation: {concrete_deps})"
                    if cfg.suggestions:
                        msg += "\n  Suggestion: Depend on abstractions (interfaces or abstract base classes), not concrete implementations."
                    if cfg.examples:
                        msg += (
                            "\n  Example:"
                            "\n  # Before:"
                            f"\n  class {node.name}:\n    def __init__(self):\n        self.dep = Concrete()"
                            "\n  # After:"
                            f"\n  class {node.name}:\n    def __init__(self, dep: AbstractDep):\n        self.dep = dep"
                        )
                    warnings.append(msg)
                    is_valid = False
        return is_valid

    def add_arguments(self) -> None:
        """Add CLI arguments to the parser (if used as a CLI tool)."""
        pass

    def run(self, dry_run: bool = False) -> ValidationResult:
        """Run the validator, supporting dry-run mode."""
        import logging

        logger = logging.getLogger(__name__)
        if dry_run:
            logger.info("[DRY RUN] SOLIDValidator would validate SOLID principles.")
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        logger.info("Running SOLIDValidator.")
        # Example: validate current directory
        return self.validate(target=".")

    def execute(self) -> ValidationResult:
        """Standard entry point for execution."""
        return self.run(dry_run=False)

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for SOLIDValidator."
        )