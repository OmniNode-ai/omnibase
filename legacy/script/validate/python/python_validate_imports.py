#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_imports
# namespace: omninode.tools.validate_imports
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:03+00:00
# last_modified_at: 2025-04-27T18:13:03+00:00
# entrypoint: validate_imports.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_imports.py
containers.foundation.src.foundation.script.validate.validate_imports.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast
import logging
import re
from pathlib import Path
from typing import Dict, Optional, Set

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import ValidationResult, ValidatorMetadata

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ImportStandardizer:
    """Standardizes imports across the codebase."""

    EXCLUDED_DIRS = {
        "__pycache__",
        ".git",
        ".venv",
        "node_modules",
        "build",
        "dist",
        ".pytest_cache",
        ".mypy_cache",
    }
    STDLIB_PREFIXES = {
        "abc",
        "argparse",
        "asyncio",
        "collections",
        "contextlib",
        "copy",
        "dataclasses",
        "datetime",
        "enum",
        "functools",
        "io",
        "json",
        "logging",
        "math",
        "os",
        "pathlib",
        "random",
        "re",
        "re",
        "sys",
        "time",
        "typing",
        "uuid",
        "warnings",
        "urllib",
        "click",
        "pytest",
        "tabulate",
        "prometheus_client",
        "starlette",
        "psycopg2",
        "alembic",
        "crewai",
        "langchain",
        "supabase",
        "croniter",
        "structlog",
        "pythonjsonlogger",
    }

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.container_name = self.root_dir.name
        self.modified_files: Set[str] = set()

    def should_process_file(self, file_path: Path) -> bool:
        if not file_path.suffix == ".py":
            return False

        for excluded in self.EXCLUDED_DIRS:
            if excluded in file_path.parts:
                return False

        return True

    def is_stdlib_or_thirdparty(self, module_name: str) -> bool:
        first_part = module_name.split(".")[0]
        return first_part in self.STDLIB_PREFIXES

    def standardize_import(self, import_path: str, file_path: Path) -> str:
        if self.is_stdlib_or_thirdparty(import_path):
            return import_path

        # If it's already an absolute import starting with 'containers', keep it
        if import_path.startswith("containers."):
            return import_path

        # If it's a relative import starting with foundation, make it absolute
        if import_path.startswith("foundation."):
            return f"containers.{self.container_name}.{import_path}"

        # For other relative imports, try to make them absolute
        rel_path = file_path.relative_to(self.root_dir)
        module_parts = list(rel_path.parent.parts)

        if "src" in module_parts:
            src_idx = module_parts.index("src")
            module_parts = module_parts[src_idx + 1 :]

        if module_parts and module_parts[0] == self.container_name:
            module_parts = module_parts[1:]

        absolute_path = ".".join(["containers", self.container_name] + module_parts)
        if absolute_path.endswith("."):
            absolute_path = absolute_path[:-1]

        if import_path.startswith("."):
            # Handle relative imports
            dots = len(re.match(r"\.+", import_path).group())
            for _ in range(dots - 1):
                if module_parts:
                    module_parts.pop()
            import_path = import_path[dots:]
            if import_path:
                module_parts.append(import_path)
            return ".".join(["containers", self.container_name] + module_parts)

        return f"containers.{self.container_name}.{import_path}"

    def fix_imports(self, file_path: Path) -> None:
        try:
            with open(file_path, "r") as f:
                content = f.read()

            tree = ast.parse(content)
            lines = content.splitlines()
            changes: Dict[tuple[int, int], str] = {}

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if not self.is_stdlib_or_thirdparty(name.name):
                            new_name = self.standardize_import(name.name, file_path)
                            if new_name != name.name:
                                # Get the indentation of the original line
                                original_line = lines[node.lineno - 1]
                                indentation = len(original_line) - len(
                                    original_line.lstrip()
                                )
                                changes[(node.lineno, node.col_offset)] = (
                                    " " * indentation + f"import {new_name}"
                                )
                elif isinstance(node, ast.ImportFrom):
                    if node.module and not self.is_stdlib_or_thirdparty(node.module):
                        new_module = self.standardize_import(node.module, file_path)
                        if new_module != node.module:
                            # Get the indentation of the original line
                            original_line = lines[node.lineno - 1]
                            indentation = len(original_line) - len(
                                original_line.lstrip()
                            )
                            names = ", ".join(n.name for n in node.names)
                            changes[(node.lineno, node.col_offset)] = (
                                " " * indentation + f"from {new_module} import {names}"
                            )

            if changes:
                new_lines = lines.copy()
                for (lineno, _), new_import in sorted(changes.items(), reverse=True):
                    new_lines[lineno - 1] = new_import

                new_content = "\n".join(new_lines)
                with open(file_path, "w") as f:
                    f.write(new_content)

                self.modified_files.add(str(file_path))
                logger.info(f"Standardized imports in {file_path}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")

    def process_directory(self) -> None:
        for file_path in Path(self.root_dir).rglob("*.py"):
            if self.should_process_file(file_path):
                self.fix_imports(file_path)


def main(root_dir: str) -> None:
    standardizer = ImportStandardizer(root_dir)
    standardizer.process_directory()

    if standardizer.modified_files:
        logger.info("\nModified files:")
        for file in sorted(standardizer.modified_files):
            logger.info(f"  - {file}")
    else:
        logger.info("No files needed modification.")


if __name__ == "__main__":
    import logging
    import sys

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    if len(sys.argv) != 2:
        logger.error("Usage: python standardize_imports.py <root_directory>")
        sys.exit(1)

    main(sys.argv[1])


    name="imports",
    version="v1",
    group="imports",
    description="Standardizes and validates import statements across the codebase.",
)
class ImportsValidator(ProtocolValidate):
    def get_name(self) -> str:
        return "imports"

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="imports",
            group="imports",
            description="Standardizes and validates import statements across the codebase.",
            version="v1",
        )

    def validate(self, target: Path, config: Optional[dict] = None):
        # This is a stub: in practice, you would call the main() logic and parse results
        # For now, just return a dummy result for registry completeness
        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            version="v1",
        )

    def _validate(self, *args, **kwargs):
        # Satisfy abstract method requirement
        return self.validate(*args, **kwargs)
