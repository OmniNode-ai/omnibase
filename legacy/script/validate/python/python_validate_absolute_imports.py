#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_absolute_imports
# namespace: omninode.tools.validate_absolute_imports
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:55+00:00
# last_modified_at: 2025-04-27T18:12:55+00:00
# entrypoint: validate_absolute_imports.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_absolute_imports.py containers.foundation.src.foundation.script.va
lidation.validate_absolute_imports.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import logging
import re
from pathlib import Path
from typing import Any, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import ValidationIssue, ValidatorMetadata
from foundation.di.di_container import DIContainer
from foundation.protocol.protocol_logger import ProtocolLogger

FOUNDATION_SRC = Path(__file__).parents[4] / "src" / "foundation"
FOUNDATION_TESTS = Path(__file__).parents[4] / "tests"

REL_IMPORT_PATTERN = re.compile(r"^\s*from\s+\.+")


def scan_for_relative_imports(root: Path) -> list[tuple[Path, int, str]]:
    violations = []
    for py_file in root.rglob("*.py"):
        with open(py_file, "r") as f:
            for i, line in enumerate(f, 1):
                if REL_IMPORT_PATTERN.match(line):
                    violations.append((py_file, i, line.strip()))
    return violations


class AbsoluteImportsValidator(ProtocolValidate):
    def __init__(self, logger: Optional[ProtocolLogger] = None, **dependencies: Any) -> None:
        super().__init__(**dependencies)
        if logger is not None:
            self.logger = logger
        else:
            # Fallback to DI container if available
            try:
                container = dependencies.get("container") or DIContainer()
                self.logger = container.resolve(ProtocolLogger)
            except Exception:
                import logging

                self.logger = logging.getLogger(__name__)

    def get_name(self) -> str:
        return "absolute_imports"

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="absolute_imports",
            group="imports",
            description="Validates that only absolute imports are used in foundation src and tests.",
            version="v1",
        )

    def validate(self, target: Any) -> bool:
        """Override base class. Returns True if no relative imports found, else False."""
        # Accept Path or directory as target
        path = target if isinstance(target, Path) else Path(str(target))
        self.errors.clear()
        self.warnings.clear()
        is_valid = True
        targets = []
        if path.is_file():
            targets = [path]
        elif path.is_dir():
            targets = list(path.rglob("*.py"))
        else:
            targets = [FOUNDATION_SRC, FOUNDATION_TESTS]
        for py_file in targets:
            if py_file.exists() and py_file.is_file():
                with open(py_file, "r") as f:
                    for i, line in enumerate(f, 1):
                        if REL_IMPORT_PATTERN.match(line):
                            self.errors.append(
                                ValidationIssue(
                                    message=f"Relative import detected: {line.strip()}",
                                    file=str(py_file),
                                    line=i,
                                    type="error",
                                )
                            )
                            is_valid = False
                            self.logger.error(
                                f"Relative import detected: {py_file}:{i}: {line.strip()}"
                            )
        return is_valid

    def _validate(self, target: Path) -> bool:
        result = self.validate(target)
        return (
            result["is_valid"]
            if isinstance(result, dict) and "is_valid" in result
            else False
        )


def main() -> None:

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    roots = [FOUNDATION_SRC, FOUNDATION_TESTS]
    all_violations = []
    for root in roots:
        if root.exists():
            all_violations.extend(scan_for_relative_imports(root))
    if all_violations:
        logger.error("[FAIL] Relative imports detected:")
        for file, line_num, line in all_violations:
            logger.error(f"  {file}:{line_num}: {line}")
        exit(1)
    else:
        logger.info("[PASS] No relative imports found in foundation src or tests.")


if __name__ == "__main__":
    main()
