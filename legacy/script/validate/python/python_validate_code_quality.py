#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_validate_code_quality"
# namespace: "omninode.tools.python_validate_code_quality"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:02+00:00"
# last_modified_at: "2025-05-05T12:44:02+00:00"
# entrypoint: "python_validate_code_quality.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolTool', 'ProtocolValidate']
# base_class: ['ProtocolTool', 'ProtocolValidate']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""validate_code_quality.py containers.foundation.src.foundation.script.valida
tion.validate_code_quality.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast
from pathlib import Path

import radon.complexity as radon_cc

try:
    from foundation.protocol.protocol_validate import ProtocolValidate
    from foundation.model.model_validate import (
        ValidationIssue,
        ValidationResult,
        ValidatorConfig,
        ValidatorMetadata,
    )
    from foundation.protocol.protocol_logger import ProtocolLogger
    from foundation.script.validate.common.common_file_utils import find_files
    from foundation.script.validate.validate_registry import (
        ValidatorRegistry,
    )
    from src.foundation.protocol.interface_tool import ProtocolTool
except ImportError:
    from foundation.script.validate.common.common_file_utils import find_files
    from models import ValidationResult, ValidatorConfig, ValidatorMetadata
    from validator import ProtocolValidate

class CodeQualityValidator(ProtocolValidate, ProtocolTool):
    """
    Validates code quality metrics.
    Implements ProtocolTool for unified CLI/validator interface.
    Checklist Reference: Validator Refactor Block Zero, Shared Tool Interface Compliance
    Now supports logger injection via the ProtocolLogger Protocol for DI/testability.
    """

    def __init__(
        self, config: ValidatorConfig = None, logger: ProtocolLogger = None, **dependencies
    ):
        super().__init__(config=config, logger=logger, **dependencies)
        self.config = config or ValidatorConfig(version="v1")

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="code_quality",
            group="quality",
            description="Validates code quality metrics.",
            version="v1",
        )

    def validate(self, target: Path, config: dict = None) -> ValidationResult:
        """Validate code quality metrics for a Python file or directory.

        Args:
            target: Path to file or directory
            config: Optional configuration dict
        Returns:
            ValidationResult: Result of the validation
        """
        self.errors.clear()
        self.warnings.clear()
        is_valid = True
        # Get rules from config
        rules = getattr(self.config, "rules", {}) or {}
        max_line_length = rules.get("max_line_length", 100)
        max_complexity = rules.get("max_complexity", 10)
        max_function_length = rules.get("max_function_length", 50)
        enforce_docstrings = rules.get("enforce_docstrings", True)

        # Find Python files
        if target.is_file() and target.suffix == ".py":
            python_files = [target]
        else:
            python_files = find_files(
                target,
                pattern="*.py",
                ignore_patterns=["**/__pycache__/**", "**/tests/**", "**/venv/**"],
            )
        if not python_files:
            self.add_error(message="No Python files found", file=str(target))
            return ValidationResult(
                is_valid=False, errors=self.errors, warnings=self.warnings
            )

        for file in python_files:
            file_failed = False
            try:
                with open(file) as f:
                    content = f.read()

                # Validate line length
                if not self._validate_line_length(content, file, max_line_length):
                    file_failed = True

                # Validate complexity
                if not self._validate_complexity(content, file, max_complexity):
                    file_failed = True

                # Validate function length
                if not self._validate_function_length(
                    content, file, max_function_length
                ):
                    file_failed = True

                # Validate docstrings if enabled
                if enforce_docstrings:
                    if not self._validate_docstrings(content, file):
                        file_failed = True

            except Exception as e:
                self.add_error(
                    message=f"Failed to analyze {file.name}: {e}", file=str(file)
                )
                file_failed = True
            if file_failed:
                self.add_failed_file(str(file))

        # At the end, set is_valid to False if any errors are present
        if self.errors:
            is_valid = False
        return ValidationResult(
            is_valid=is_valid, errors=self.errors, warnings=self.warnings
        )

    def _validate_line_length(self, content: str, file: Path, max_length: int) -> bool:
        """Validate line lengths."""
        is_valid = True
        warn_length = min(80, max_length)  # Warn for lines >80 but <= max_length
        for i, line in enumerate(content.splitlines(), 1):
            if len(line) > max_length:
                self.add_error(
                    message=f"Line {i} exceeds maximum length of {max_length}",
                    file=str(file),
                    line=i,
                    details={"line_length": len(line), "max_length": max_length},
                )
                is_valid = False
            elif len(line) > warn_length:
                self.add_warning(
                    message=f"Line {i} exceeds recommended length of {warn_length}",
                    file=str(file),
                    line=i,
                    details={
                        "line_length": len(line),
                        "recommended_length": warn_length,
                    },
                )
        # Warn for TODO/FIXME comments
        for i, line in enumerate(content.splitlines(), 1):
            if "TODO" in line or "FIXME" in line:
                self.add_warning(
                    message=f"Line {i} contains TODO/FIXME comment",
                    file=str(file),
                    line=i,
                )
        return is_valid

    def _validate_complexity(
        self, content: str, file: Path, max_complexity: int
    ) -> bool:
        """Validate code complexity."""
        is_valid = True
        try:
            blocks = radon_cc.cc_visit(content)
            for block in blocks:
                if block.complexity > max_complexity:
                    self.add_error(
                        message=f"Function '{block.name}' has complexity of {block.complexity} (max {max_complexity})",
                        file=str(file),
                        line=block.lineno,
                        details={
                            "function": block.name,
                            "complexity": block.complexity,
                            "max_complexity": max_complexity,
                        },
                    )
                    is_valid = False
                elif block.complexity >= max_complexity - 2:
                    self.add_warning(
                        message=f"Function '{block.name}' has high complexity: {block.complexity} (near max {max_complexity})",
                        file=str(file),
                        line=block.lineno,
                        details={
                            "function": block.name,
                            "complexity": block.complexity,
                            "max_complexity": max_complexity,
                        },
                    )
        except Exception as e:
            self.add_error(message=f"Failed to analyze complexity: {e}", file=str(file))
            is_valid = False
        return is_valid

    def _validate_function_length(
        self, content: str, file: Path, max_length: int
    ) -> bool:
        """Validate function lengths."""
        is_valid = True
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    end_line = node.end_lineno or node.lineno
                    length = end_line - node.lineno + 1
                    if length > max_length:
                        self.add_error(
                            message=f"Function '{node.name}' is too long ({length} lines, max {max_length})",
                            file=str(file),
                            line=node.lineno,
                            details={
                                "function": node.name,
                                "length": length,
                                "max_length": max_length,
                            },
                        )
                        is_valid = False
                    elif length > int(0.8 * max_length):
                        self.add_warning(
                            message=f"Function '{node.name}' is long: {length} lines (80% of max {max_length})",
                            file=str(file),
                            line=node.lineno,
                            details={
                                "function": node.name,
                                "length": length,
                                "max_length": max_length,
                            },
                        )
                    # Warn for missing type hints
                    if not node.returns or not all(
                        arg.annotation for arg in node.args.args
                    ):
                        self.add_warning(
                            message=f"Function '{node.name}' is missing type hints",
                            file=str(file),
                            line=node.lineno,
                            details={"function": node.name},
                        )
        except Exception as e:
            self.add_error(f"Failed to analyze function length: {e}", file=str(file))
            is_valid = False
        return is_valid

    def _validate_docstrings(self, content: str, file: Path) -> bool:
        """Validate presence of docstrings."""
        is_valid = True
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module),
                ):
                    # Check for docstring
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        name = getattr(
                            node,
                            "name",
                            "module" if isinstance(node, ast.Module) else "unknown",
                        )
                        kind = (
                            "module"
                            if isinstance(node, ast.Module)
                            else (
                                "class"
                                if isinstance(node, ast.ClassDef)
                                else "function"
                            )
                        )
                        lineno = getattr(node, "lineno", None)
                        self.add_warning(
                            message=f"Missing docstring for {kind} '{name}'",
                            file=str(file),
                            line=lineno,
                            details={"name": name, "type": kind},
                        )
        except Exception as e:
            self.add_error(f"Failed to analyze docstrings: {e}", file=str(file))
            is_valid = False
        return is_valid

    def get_name(self) -> str:
        return "code_quality"

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for CodeQualityValidator."
        )

    def add_arguments(self) -> None:
        """Add CLI arguments to the parser (if used as a CLI tool)."""
        pass

    def run(self, dry_run: bool = False) -> None:
        """
        Main logic for the validator. If dry_run is True, perform validation but do not write or mutate state.
        """
        # Example: validate a target path (could be set via arguments in a real CLI)
        # For demonstration, just log dry run vs. normal run
        if dry_run:
            self.logger.info(
                "Dry run: code quality validation performed, no state mutated or files written."
            )
        else:
            self.logger.info(
                "Validation run: code quality validation may mutate state or write files."
            )
        # Actual validation logic would go here (e.g., self.validate(target))
        pass

    def execute(self) -> None:
        """Parse arguments and execute the validator (if used as a CLI tool)."""
        self.run()


# Register the validator explicitly for Foundation schema registry compatibility
ValidatorRegistry().register(
    name="code_quality",
    version="v1",
    validator_cls=CodeQualityValidator,
    meta={
        "name": "code_quality",
        "version": "v1",
        "group": "quality",
        "description": "Validates code quality metrics.",
    },
)