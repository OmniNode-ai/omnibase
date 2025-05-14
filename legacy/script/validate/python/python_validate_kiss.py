#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_kiss
# namespace: omninode.tools.validate_kiss
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:02+00:00
# last_modified_at: 2025-04-27T18:13:02+00:00
# entrypoint: validate_kiss.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_kiss.py
containers.foundation.src.foundation.script.validate.validate_kiss.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast
import logging
from pathlib import Path
from typing import List, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from foundation.protocol.protocol_tool import ProtocolTool


class KISSValidatorConfig(ValidatorConfig):
    version: str = "v1"
    max_cyclomatic_complexity: int = 10
    max_nesting_depth: int = 3
    max_params: int = 5
    exclude_dirs: List[str] = []


class KISSValidator(ProtocolValidate, ProtocolTool):
    """Flags overly complex code and suggests simplification. Implements ProtocolTool."""

    def __init__(self, config: Optional[dict] = None, **dependencies):
        # Accept config as either a dict or a KISSValidatorConfig instance.
        # Always pass a dict to ProtocolValidate (for .get()), always set self.pydantic_config to a KISSValidatorConfig instance.
        # All internal logic should use self.pydantic_config for type safety.
        if isinstance(config, KISSValidatorConfig):
            self.pydantic_config = config
            config_dict = (
                config.model_dump() if hasattr(config, "model_dump") else config.dict()
            )
        else:
            self.pydantic_config = KISSValidatorConfig(**(config or {}))
            config_dict = (
                self.pydantic_config.model_dump()
                if hasattr(self.pydantic_config, "model_dump")
                else self.pydantic_config.dict()
            )
        super().__init__(config_dict, **dependencies)
        self.config = (
            self.pydantic_config
        )  # For backward compatibility, but use self.pydantic_config in this class.

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="kiss",
            group="quality",
            description="Flags overly complex code and suggests simplification.",
            version="v1",
        )

    def get_name(self) -> str:
        return "kiss"

    def validate(
        self, target: Path, config: Optional[KISSValidatorConfig] = None
    ) -> ValidationResult:
        logger = logging.getLogger(__name__)
        cfg = config or self.config
        logger.info(f"KISSValidator.validate called with target={target}")
        logger.info(
            f"Config: max_cyclomatic_complexity={cfg.max_cyclomatic_complexity}, max_nesting_depth={cfg.max_nesting_depth}, max_params={cfg.max_params}, exclude_dirs={cfg.exclude_dirs}"
        )
        errors = []
        warnings = []
        suggestions = []
        is_valid = True
        python_files = [
            f
            for f in target.rglob("*.py")
            if not any(ex in f.parts for ex in cfg.exclude_dirs)
        ]
        logger.info(
            f"Found {len(python_files)} Python files: {[str(f) for f in python_files]}"
        )
        for file in python_files:
            try:
                logger.info(f"Parsing file: {file}")
                with open(file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=str(file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Cyclomatic complexity
                        complexity = self._cyclomatic_complexity(node)
                        if complexity > cfg.max_cyclomatic_complexity:
                            is_valid = False
                            msg = f"{file}:{node.lineno}: Function '{node.name}' has cyclomatic complexity {complexity} (max allowed: {cfg.max_cyclomatic_complexity})"
                            logger.warning(msg)
                            errors.append(
                                ValidationIssue(
                                    message=msg,
                                    file=str(file),
                                    line=node.lineno,
                                    type="error",
                                )
                            )
                            suggestions.append(
                                f"simplification: reduce cyclomatic complexity in '{node.name}' by reducing branches, splitting into smaller functions, or removing unnecessary logic."
                            )
                        # Nesting depth
                        depth = self._max_nesting_depth(node)
                        if depth > cfg.max_nesting_depth:
                            is_valid = False
                            msg = f"{file}:{node.lineno}: Function '{node.name}' has nesting depth {depth} (max allowed: {cfg.max_nesting_depth})"
                            logger.warning(msg)
                            errors.append(
                                ValidationIssue(
                                    message=msg,
                                    file=str(file),
                                    line=node.lineno,
                                    type="error",
                                )
                            )
                            suggestions.append(
                                f"refactor: reduce nesting in '{node.name}' (e.g., early returns, helper functions)."
                            )
                        # Parameter count
                        num_params = len(node.args.args)
                        if num_params > cfg.max_params:
                            is_valid = False
                            msg = f"{file}:{node.lineno}: Function '{node.name}' has {num_params} parameters (max allowed: {cfg.max_params})"
                            logger.warning(msg)
                            errors.append(
                                ValidationIssue(
                                    message=msg,
                                    file=str(file),
                                    line=node.lineno,
                                    type="error",
                                )
                            )
                            suggestions.append(
                                f"Reduce the number of parameters for '{node.name}' (group related params, use objects, or refactor logic)."
                            )
            except Exception as e:
                warn_msg = f"Could not parse {file}: {e}"
                logger.error(warn_msg)
                warnings.append(
                    ValidationIssue(message=warn_msg, file=str(file), type="warning")
                )
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            version=cfg.version,
        )

    def _cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        # Simple cyclomatic complexity: 1 + number of branches
        complexity = 1
        for n in ast.walk(node):
            if isinstance(
                n,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.And,
                    ast.Or,
                    ast.ExceptHandler,
                    ast.With,
                    ast.Try,
                    ast.BoolOp,
                    ast.IfExp,
                ),
            ):
                complexity += 1
        return complexity

    def _max_nesting_depth(self, node: ast.FunctionDef) -> int:
        def depth(n, current=0):
            if not hasattr(n, "body") or not isinstance(n.body, list):
                return current
            if not n.body:
                return current
            return max(
                [
                    depth(child, current + 1)
                    for child in n.body
                    if isinstance(child, ast.AST)
                ]
                + [current]
            )

        return depth(node, 0)

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for KISSValidator."
        )

    def add_arguments(self) -> None:
        """Add CLI arguments to the parser (if used as a CLI tool)."""
        pass

    def run(self, dry_run: bool = False) -> ValidationResult:
        """Run the validator, supporting dry-run mode."""
        import logging

        logger = logging.getLogger(__name__)
        if dry_run:
            logger.info("[DRY RUN] KISSValidator would validate for KISS violations.")
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        logger.info("Running KISSValidator.")
        # Example: validate current directory
        return self.validate(target=".")

    def execute(self) -> ValidationResult:
        """Standard entry point for execution."""
        return self.run(dry_run=False)
