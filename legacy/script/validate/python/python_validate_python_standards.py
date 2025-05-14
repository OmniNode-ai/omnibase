#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_python_standards
# namespace: omninode.tools.validate_python_standards
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:04+00:00
# last_modified_at: 2025-04-27T18:13:04+00:00
# entrypoint: validate_python_standards.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_python_standards.py containers.foundation.src.foundation.script.va
lidation.validate_python_standards.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast
import logging
import os
import re
from pathlib import Path
from typing import List

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from pydantic import Field


def ensure_directory(path):
    """Ensure directory exists."""
    os.makedirs(path, exist_ok=True)


def copy_template(template_path, target_path, replacements=None):
    """Copy template file with optional replacements."""
    if not os.path.exists(template_path):
        logging.getLogger(__name__).error(f"Template not found: {template_path}")
        return False

    # Create target directory if it doesn't exist
    target_dir = os.path.dirname(target_path)
    if target_dir:  # Only create directory if path is not empty
        os.makedirs(target_dir, exist_ok=True)

    with open(template_path, "r") as f:
        content = f.read()

    if replacements:
        for key, value in replacements.items():
            content = content.replace(key, value)

    with open(target_path, "w") as f:
        f.write(content)

    return True


def fix_markdown_files():
    """Fix markdown files by applying the README template."""
    template_path = "templates/README_TEMPLATE.md"

    # Find all markdown files
    markdown_files = []
    for ext in ["*.md", "*.MD"]:
        markdown_files.extend(glob.glob(f"**/{ext}", recursive=True))

    for md_file in markdown_files:
        if "templates" in md_file or "venv" in md_file:
            continue

        # Get component name from directory structure or filename
        component_name = os.path.basename(os.path.dirname(md_file))
        if component_name == "." or not component_name:
            component_name = os.path.splitext(os.path.basename(md_file))[0]

        logging.getLogger(__name__).info(f"Fixing markdown file: {md_file}")
        copy_template(
            template_path,
            md_file,
            {"[Component Name]": component_name.replace("-", " ").title()},
        )


def fix_dockerfiles():
    """Fix Dockerfiles by applying the Dockerfile template."""
    template_path = "templates/DOCKERFILE_TEMPLATE"

    # Find all Dockerfiles
    dockerfiles = glob.glob("**/Dockerfile", recursive=True)

    for dockerfile in dockerfiles:
        if "templates" in dockerfile:
            continue

        logging.getLogger(__name__).info(f"Fixing Dockerfile: {dockerfile}")
        copy_template(
            template_path,
            dockerfile,
            {
                "dev@example.com": "dev@aidev.com",
                "Description of the service": f"Service for {os.path.basename(os.path.dirname(dockerfile))}",
            },
        )


def fix_api_endpoints():
    """Fix API endpoints by adding health and version endpoints."""
    template_path = "templates/API_ENDPOINTS_TEMPLATE.py"

    # Find all Python files that might contain API endpoints
    api_files = []
    for pattern in ["**/api/*.py", "**/routes/*.py"]:
        api_files.extend(glob.glob(pattern, recursive=True))

    for api_file in api_files:
        if (
            "templates" in api_file
            or "__pycache__" in api_file
            or "schemas" in api_file
            or "venv" in api_file
        ):
            continue

        logging.getLogger(__name__).info(
            f"Adding health/version endpoints to: {api_file}"
        )
        # For now, we'll just copy the template - in a real implementation,
        # we'd want to merge with existing endpoints
        copy_template(template_path, api_file)


class PythonStandardsValidatorConfig(ValidatorConfig):
    version: str = "v1"
    forbidden_patterns: List[str] = Field(
        default_factory=lambda: [
            r"print\s*\(",
            r"import\s+pdb",
            r"breakpoint\s*\(",
            r"TODO",
            r"FIXME",
        ]
    )
    required_endpoints: List[str] = Field(default_factory=lambda: ["health", "version"])
    forbidden_files: List[str] = Field(
        default_factory=lambda: [".DS_Store", "__pycache__"]
    )


    name="python_standards",
    version="v1",
    group="python",
    description="Validates Python project standards: forbidden patterns, API endpoints, forbidden files.",
)
class PythonStandardsValidator(ProtocolValidate):
    """Validates Python project standards: forbidden patterns, API endpoints, forbidden files."""

    def __init__(self, config=None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = PythonStandardsValidatorConfig(**(config or {}))
        self.logger = dependencies.get("logger") or logging.getLogger(__name__)

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="python_standards",
            group="python",
            description="Validates Python project standards: forbidden patterns, API endpoints, forbidden files.",
            version="v1",
        )

    def get_name(self) -> str:
        return "python_standards"

    def validate(self, target: Path, config: PythonStandardsValidatorConfig = None):
        cfg = config or self.config
        python_files = list(target.rglob("*.py")) if target.is_dir() else [target]
        for file in python_files:
            file_failed = False
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                for pattern in cfg.forbidden_patterns:
                    for match in re.finditer(pattern, content):
                        line_number = content[: match.start()].count("\n") + 1
                        self.errors.append(
                            ValidationIssue(
                                message=f"Forbidden pattern '{pattern}' found in {file} at line {line_number}",
                                file=str(file),
                                line=line_number,
                            )
                        )
                        file_failed = True
            except Exception as e:
                self.errors.append(
                    ValidationIssue(
                        message=f"Failed to analyze {file}: {e}", file=str(file)
                    )
                )
                file_failed = True
            if file_failed:
                self.add_failed_file(str(file))
        # 2. Check required API endpoints in likely API modules only (using AST for function defs)
        for file in python_files:
            parent_dirs = {p.name for p in file.parents}
            debug_msg = f"Checking file: {file} | parent_dirs: {parent_dirs} | name: {file.name}"
            logging.getLogger(__name__).debug(debug_msg)
            file_failed = False
            if (
                "api" in parent_dirs
                or "routes" in parent_dirs
                or "service" in parent_dirs
                or file.name.startswith("api_")
            ):
                logging.getLogger(__name__).info(
                    f"  -> Endpoint check triggered for: {file}"
                )
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        content = f.read()
                    try:
                        tree = ast.parse(content)
                        func_names = {
                            node.name
                            for node in ast.walk(tree)
                            if isinstance(node, ast.FunctionDef)
                        }
                    except Exception as e:
                        self.errors.append(
                            ValidationIssue(
                                message=f"Failed to parse AST for {file}: {e}",
                                file=str(file),
                            )
                        )
                        file_failed = True
                        continue
                    missing_endpoints = [
                        endpoint
                        for endpoint in cfg.required_endpoints
                        if endpoint not in func_names
                    ]
                    for endpoint in missing_endpoints:
                        self.errors.append(
                            ValidationIssue(
                                message=f"Required API endpoint function '{endpoint}' not found in {file}",
                                file=str(file),
                            )
                        )
                        file_failed = True
                except Exception as e:
                    self.errors.append(
                        ValidationIssue(
                            message=f"Failed to analyze {file}: {e}", file=str(file)
                        )
                    )
                    file_failed = True
            else:
                logging.getLogger(__name__).info(
                    f"  -> Endpoint check NOT triggered for: {file}"
                )
            if file_failed:
                self.add_failed_file(str(file))
        # 3. Check for forbidden files/directories
        for root, dirs, files in os.walk(target):
            for forbidden in cfg.forbidden_files:
                if forbidden in files or forbidden in dirs:
                    self.errors.append(
                        ValidationIssue(
                            message=f"Forbidden file or directory '{forbidden}' found in {root}",
                            file=str(root),
                        )
                    )
        return ValidationResult(
            is_valid=not self.errors,
            errors=self.errors,
            warnings=self.warnings,
            version=self.config.version,
        )

    def _validate(self, target: Path) -> bool:
        result = self.validate(target)
        return result.is_valid


def main():
    """Main function to fix standards violations."""
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    # Ensure templates directory exists
    ensure_directory("templates")

    # Fix markdown files
    fix_markdown_files()

    # Fix Dockerfiles
    fix_dockerfiles()

    # Fix API endpoints
    fix_api_endpoints()

    logger.info("Standards fixes applied. Please review the changes before committing.")


if __name__ == "__main__":
    import argparse
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(description="Validate Python project standards")
    parser.add_argument(
        "path", type=str, nargs="?", default=".", help="Path to project root or file"
    )
    args = parser.parse_args()
    validator = PythonStandardsValidator()
    result = validator.validate(Path(args.path))
    if not result.is_valid:
        logger.error("Python standards validation FAILED:")
        for err in result.errors:
            logger.error(f"  - {err}")
        for warn in result.warnings:
            logger.warning(f"  - Warning: {warn}")
        exit(1)
    else:
        logger.info("Python standards validation PASSED.")
        exit(0)
