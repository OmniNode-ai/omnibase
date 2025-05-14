#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_dry
# namespace: omninode.tools.validate_dry
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:59+00:00
# last_modified_at: 2025-04-27T18:12:59+00:00
# entrypoint: validate_dry.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_dry.py
containers.foundation.src.foundation.script.validate.validate_dry.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)


class DRYValidatorConfig(ValidatorConfig):
    version: str = "v1"
    min_lines: int = 5  # Minimum lines for a block to be considered for duplication
    min_occurrences: int = (
        2  # Minimum number of times a block must appear to be flagged
    )
    exclude_dirs: List[str] = []
    ignore_comments: bool = True


    name="dry",
    version="v1",
    group="quality",
    description="Detects code duplication and suggests refactoring.",
)
class DRYValidator(ProtocolValidate):
    """Detects code duplication and suggests refactoring."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = DRYValidatorConfig(**(config or {}))

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="dry",
            group="quality",
            description="Detects code duplication and suggests refactoring.",
            version="v1",
        )

    def get_name(self) -> str:
        return "dry"

    def validate(
        self, target: Path, config: Optional[DRYValidatorConfig] = None
    ) -> ValidationResult:
        cfg = config or self.config
        self.errors.clear()
        self.warnings.clear()
        is_valid = True
        block_map = defaultdict(list)  # hash -> list of (file, lineno, code)
        # Scan all .py files
        python_files = [
            f
            for f in target.rglob("*.py")
            if not any(ex in f.parts for ex in cfg.exclude_dirs)
        ]
        for file in python_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                # Optionally ignore comments
                if cfg.ignore_comments:
                    code_lines = [l for l in lines if not l.strip().startswith("#")]
                else:
                    code_lines = lines
                # Only process if enough lines for a block
                if len(code_lines) < cfg.min_lines:
                    continue
                # Sliding window of min_lines
                for i in range(len(code_lines) - cfg.min_lines + 1):
                    block = code_lines[i : i + cfg.min_lines]
                    # Only consider blocks that are exactly min_lines in length
                    if len(block) < cfg.min_lines:
                        continue
                    block_str = "".join(block).strip()
                    if not block_str:
                        continue
                    block_hash = hashlib.sha256(block_str.encode()).hexdigest()
                    block_map[block_hash].append((file, i + 1, block_str))
            except Exception as e:
                self.warnings.append(
                    ValidationIssue(
                        message=f"Could not parse {file}: {e}",
                        file=str(file),
                        type="warning",
                    )
                )
        # Only flag duplicates if at least min_occurrences files have a block of at least min_lines lines
        for block_hash, occurrences in block_map.items():
            if len(occurrences) >= cfg.min_occurrences and all(
                len(occ[2].splitlines()) >= cfg.min_lines for occ in occurrences
            ):
                is_valid = False
                files_lines = [(str(f), lineno) for f, lineno, _ in occurrences]
                files_lines_sorted = sorted(files_lines, key=lambda x: (x[0], x[1]))
                msg = f"Duplicate code block found in: {files_lines_sorted}"
                suggestion = "Consider refactoring repeated code into a function, method, or module."
                self.errors.append(
                    ValidationIssue(
                        message=msg,
                        details={"files_lines": files_lines_sorted},
                        file=files_lines_sorted[0][0] if files_lines_sorted else "",
                        type="error",
                    )
                )
                # Optionally, add suggestions as warnings or a separate suggestions list if needed
        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            version=cfg.version,
        )

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for DRYValidator."
        )
