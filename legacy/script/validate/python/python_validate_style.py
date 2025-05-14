#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_validate_style"
# namespace: "omninode.tools.python_validate_style"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:02+00:00"
# last_modified_at: "2025-05-05T12:44:02+00:00"
# entrypoint: "python_validate_style.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolValidate', 'ValidatorConfig']
# base_class: ['ProtocolValidate', 'ValidatorConfig']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""validate_style.py
containers.foundation.src.foundation.script.validate.validate_style.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import tokenize
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from foundation.script.validate.common.common_file_utils import find_files


class StyleCheckerConfig(ValidatorConfig):
    version: str = "v1"
    indent_size: int = 4
    use_spaces: bool = True
    enforce_newline_at_eof: bool = True
    max_blank_lines: int = 2


class StyleChecker(ProtocolValidate):
    """Validates code style and formatting."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = StyleCheckerConfig(**(config or {}))

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="style_checker",
            group="style",
            description="Validates code style and formatting.",
            version="v1",
        )

    def get_name(self) -> str:
        return "style"

    def validate(
        self, target: Path, config: Optional[StyleCheckerConfig] = None
    ) -> ValidationResult:
        cfg = config or self.config
        # Find Python files
        python_files = []
        if target.is_file() and target.suffix == ".py":
            python_files = [target]
        else:
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
            self.add_error("No Python files found", type="error")
        for file in python_files:
            file_failed = False
            try:
                with open(file) as f:
                    content = f.read()
                if not content.strip():
                    self.add_error(
                        f"{file}: File is empty", file=str(file), type="error"
                    )
                    file_failed = True
                    continue
                if not self._validate_indentation(
                    content, file, cfg.indent_size, cfg.use_spaces, []
                ):
                    self.add_error(
                        f"{file}: Indentation error", file=str(file), type="error"
                    )
                    file_failed = True
                if not self._validate_blank_lines(
                    content, file, cfg.max_blank_lines, []
                ):
                    self.add_error(
                        f"{file}: Too many consecutive blank lines",
                        file=str(file),
                        type="error",
                    )
                    file_failed = True
                if cfg.enforce_newline_at_eof:
                    if not self._validate_eof_newline(content, file, []):
                        self.add_error(
                            f"{file}: File does not end with newline",
                            file=str(file),
                            type="error",
                        )
                        file_failed = True
                if not self._validate_whitespace(content, file, []):
                    self.add_error(
                        f"{file}: Whitespace error", file=str(file), type="error"
                    )
                    file_failed = True
            except Exception as e:
                self.add_error(
                    f"Failed to analyze {file.name}: {e}", file=str(file), type="error"
                )
                file_failed = True
            if file_failed:
                self.add_failed_file(str(file))
        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            version=cfg.version,
        )

    def _validate_indentation(
        self,
        content: str,
        file: Path,
        indent_size: int,
        use_spaces: bool,
        errors: List[str],
    ) -> bool:
        is_valid = True
        for i, line in enumerate(content.splitlines(), 1):
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip())
            if indent % indent_size != 0:
                errors.append(
                    f"{file}:{i}: Incorrect indentation (got {indent}, expected multiple of {indent_size})"
                )
                is_valid = False
            if use_spaces and "\t" in line[:indent]:
                errors.append(f"{file}:{i}: Uses tabs for indentation")
                is_valid = False
        return is_valid

    def _validate_blank_lines(
        self, content: str, file: Path, max_blank: int, errors: List[str]
    ) -> bool:
        is_valid = True
        blank_count = 0
        for i, line in enumerate(content.splitlines(), 1):
            if not line.strip():
                blank_count += 1
                if blank_count > max_blank:
                    errors.append(
                        f"{file}:{i}: Too many consecutive blank lines ({blank_count}, max {max_blank})"
                    )
                    is_valid = False
            else:
                blank_count = 0
        return is_valid

    def _validate_eof_newline(
        self, content: str, file: Path, errors: List[str]
    ) -> bool:
        if not content.endswith("\n"):
            errors.append(f"{file}: File does not end with newline")
            return False
        return True

    def _validate_whitespace(self, content: str, file: Path, errors: List[str]) -> bool:
        is_valid = True
        try:
            tokens = list(tokenize.generate_tokens(StringIO(content).readline))
            for i, token in enumerate(tokens[:-1]):
                next_token = tokens[i + 1]
                if token.type == tokenize.NEWLINE:
                    line = content.splitlines()[token.start[0] - 1]
                    if line.rstrip() != line:
                        errors.append(f"{file}:{token.start[0]}: Trailing whitespace")
                        is_valid = False
                elif token.type == tokenize.OP:
                    if token.string in {
                        "+",
                        "-",
                        "*",
                        "/",
                        "//",
                        "%",
                        "**",
                        "==",
                        "!=",
                        "<",
                        ">",
                        "<=",
                        ">=",
                        "and",
                        "or",
                    }:
                        if (
                            i > 0
                            and tokens[i - 1].end[1] == token.start[1]
                            or next_token.start[1] == token.end[1]
                        ):
                            errors.append(
                                f"{file}:{token.start[0]}: Missing space around operator '{token.string}'"
                            )
                            is_valid = False
        except Exception as e:
            errors.append(f"{file}: Failed to analyze whitespace: {e}")
            is_valid = False
        return is_valid

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for StyleChecker."
        )