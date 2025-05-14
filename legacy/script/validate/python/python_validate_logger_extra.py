#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_logger_extra
# namespace: omninode.tools.validate_logger_extra
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:01+00:00
# last_modified_at: 2025-04-27T18:13:01+00:00
# entrypoint: validate_logger_extra.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_logger_extra.py containers.foundation.src.foundation.script.valida
tion.validate_logger_extra.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import argparse
import ast
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from foundation.script.validate.common.common_validator_utils import get_staged_files
from foundation.script.validate.common.common_logger_extra import (
    ALLOW_EXTRA,
    OPTIONAL_FIELDS,
    REQUIRED_FIELDS,
)
from pydantic import Field
from foundation.model.model_validation_issue_mixin import ValidationIssueMixin


class ProtocolLoggerExtraValidatorConfig(ValidatorConfig):
    version: str = "v1"
    required: List[str] = Field(default_factory=lambda: REQUIRED_FIELDS)
    optional: List[str] = Field(default_factory=lambda: OPTIONAL_FIELDS)
    allow_extra: bool = ALLOW_EXTRA


class ProtocolLoggerExtraValidator(ValidationIssueMixin, ProtocolValidate):
    """Validates logger extra dicts are built with make_logger_extra and
    conform to schema."""

    def __init__(self, config=None, **dependencies):
        super().__init__(config, **dependencies)
        if isinstance(config, ProtocolLoggerExtraValidatorConfig):
            self.pydantic_config = config
            config_dict = (
                config.model_dump() if hasattr(config, "model_dump") else config.dict()
            )
        else:
            self.pydantic_config = ProtocolLoggerExtraValidatorConfig(**(config or {}))
            config_dict = (
                self.pydantic_config.model_dump()
                if hasattr(self.pydantic_config, "model_dump")
                else self.pydantic_config.dict()
            )
        self.config = (
            self.pydantic_config
        )  # For backward compatibility, but use self.pydantic_config in this class.
        self.logger = (
            dependencies.get("logger")
            if "logger" in dependencies
            else logging.getLogger(__name__)
        )
        self.errors: list = []
        self.warnings: list = []
        self.failed_files: list = []

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="logger_extra",
            description="Validates logger extra dicts are built with make_logger_extra and conform to schema.",
            version="v1",
        )

    def get_name(self) -> str:
        return "logger_extra"

    def validate(
        self, target: Path, config: Optional[ProtocolLoggerExtraValidatorConfig] = None
    ) -> ValidationResult:
        """Validate logger extra dicts are built with make_logger_extra and conform to schema.

        Args:
            target: Path to file or directory to check
            config: Optional configuration
        Returns:
            ValidationResult: Result of the validation
        """
        self.errors.clear()
        self.warnings.clear()
        self.failed_files.clear()
        is_valid = True
        files = []
        if target.is_file() and target.suffix == ".py":
            files = [target]
        else:
            files = [f for f in target.rglob("*.py") if f.is_file()]
        for file in files:
            file_failed = False
            with open(file, "r", encoding="utf-8") as f:
                source = f.read()
            try:
                tree = ast.parse(source, filename=str(file))
            except Exception as e:
                self.add_error(
                    message=f"Could not parse {file}: {e}", file=str(file), type="error"
                )
                is_valid = False
                file_failed = True
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    method = node.func.attr
                    if method in {
                        "debug",
                        "info",
                        "warning",
                        "error",
                        "critical",
                        "exception",
                        "log",
                    }:
                        for kw in node.keywords:
                            if kw.arg == "extra":
                                # Must be a call to make_logger_extra
                                if not (
                                    isinstance(kw.value, ast.Call)
                                    and getattr(kw.value.func, "id", None)
                                    == "make_logger_extra"
                                ):
                                    self.add_error(
                                        message=f"logger.{method}() extra must be built with make_logger_extra()",
                                        file=str(file),
                                        line=node.lineno,
                                        type="error",
                                    )
                                    is_valid = False
                                    file_failed = True
                                else:
                                    # Validate required/optional fields if possible
                                    arg_names = {
                                        k.arg for k in kw.value.keywords if k.arg
                                    }
                                    # Check for None values in required fields
                                    none_required = {
                                        k.arg
                                        for k in kw.value.keywords
                                        if k.arg in self.config.required
                                        and isinstance(k.value, ast.Constant)
                                        and k.value.value is None
                                    }
                                    missing = (
                                        set(self.config.required) - arg_names
                                    ) | none_required
                                    if missing:
                                        self.add_error(
                                            message=f"logger.{method}() extra missing required fields: {missing}",
                                            file=str(file),
                                            line=node.lineno,
                                            type="error",
                                        )
                                        is_valid = False
                                        file_failed = True
                                    if not self.config.allow_extra:
                                        allowed = set(
                                            self.config.required + self.config.optional
                                        )
                                        extras = arg_names - allowed
                                        if extras:
                                            self.add_error(
                                                message=f"logger.{method}() extra has unexpected fields: {extras}",
                                                file=str(file),
                                                line=node.lineno,
                                                type="error",
                                            )
                                            is_valid = False
                                            file_failed = True
            if file_failed:
                self.add_failed_file(str(file))
        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            version=self.config.version,
        )

    def _validate(self, target: Path) -> bool:
        result = self.validate(target)
        return result.is_valid

    def add_failed_file(self, file: str):
        self.failed_files.append(file)

    def describe_flags(self):
        """No-op for protocol compliance."""
        return None


def find_logger_violations(filename: str) -> List[str]:
    violations = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=filename)
    except Exception as e:
        return [f"[ERROR] Could not parse {filename}: {e}"]

    class ProtocolLoggerCallVisitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            # Check if this is a logger.<level>() call
            if isinstance(node.func, ast.Attribute):
                method = node.func.attr
                if method in {
                    "debug",
                    "info",
                    "warning",
                    "error",
                    "critical",
                    "exception",
                    "log",
                }:
                    # Check for keyword arguments other than 'extra'
                    for kw in node.keywords:
                        if kw.arg != "extra":
                            violations.append(
                                f"{filename}:{node.lineno}: logger.{method}() uses top-level kwarg '{kw.arg}' (should use 'extra' dict)"
                            )
            self.generic_visit(node)

    ProtocolLoggerCallVisitor().visit(tree)
    return violations


def main():
    parser = argparse.ArgumentParser(
        description="Lint for logger calls with structured fields outside 'extra'."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to check. If omitted, checks staged files.",
    )
    args = parser.parse_args()

    files = []
    if args.paths:
        for path in args.paths:
            if os.path.isdir(path):
                for root, _, filenames in os.walk(path):
                    for fname in filenames:
                        if fname.endswith(".py"):
                            files.append(os.path.join(root, fname))
            elif os.path.isfile(path) and path.endswith(".py"):
                files.append(path)
    else:
        files = get_staged_files()

    all_violations = []
    for file in files:
        all_violations.extend(find_logger_violations(file))

    if all_violations:
        print("\nProtocolLogger structured field violations detected:")
        for v in all_violations:
            print(v)
        print(
            "\nAll structured/contextual fields must be passed via the 'extra' dictionary in logger calls."
        )
        sys.exit(1)
    else:
        print("No logger structured field violations found.")
        sys.exit(0)


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()
