#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_project_standards
# namespace: omninode.tools.validate_project_standards
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:57+00:00
# last_modified_at: 2025-04-27T18:12:57+00:00
# entrypoint: validate_project_standards.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_project_standards.py containers.foundation.src.foundation.script.v
alidation.validate_project_standards.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from pydantic import Field

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

from foundation.script.validate.validate_code_quality import CodeQualityValidator
from foundation.script.validate.validate_compose import ComposeValidator

# Import sub-validators
from foundation.script.validate.validate_container import ContainerValidator
from foundation.script.validate.validate_dockerfile import DockerfileValidator
from foundation.script.validate.validate_env_secrets import EnvSecretsValidator
from foundation.script.validate.validate_logger_extra import ProtocolLoggerExtraValidator
from foundation.script.validate.validate_poetry import PoetryValidator
from foundation.script.validate.validate_security import SecurityValidator
from foundation.script.validate.validate_style import StyleChecker
from foundation.script.validate.validate_test_coverage import TestCoverageValidator


class ProjectStandardsValidatorConfig(ValidatorConfig):
    version: str = "v1"
    sub_validators: List[str] = Field(
        default_factory=lambda: [
            "container",
            "poetry",
            "dockerfile",
            "compose",
            "code_quality",
            "style",
            "test_coverage",
            "security",
            "env_secrets",
            "logger_extra",
        ]
    )
    paths: Dict[str, str] = Field(
        default_factory=dict
    )  # Optional: map sub-validator to path


class ProjectStandardsValidator(ProtocolValidate):
    """Aggregates all project standards and sub-validator results."""

    SUB_VALIDATOR_MAP = {
        "container": ContainerValidator,
        "poetry": PoetryValidator,
        "dockerfile": DockerfileValidator,
        "compose": ComposeValidator,
        "code_quality": CodeQualityValidator,
        "style": StyleChecker,
        "test_coverage": TestCoverageValidator,
        "security": SecurityValidator,
        "env_secrets": EnvSecretsValidator,
        "logger_extra": ProtocolLoggerExtraValidator,
    }

    def __init__(self, config=None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = ProjectStandardsValidatorConfig(**(config or {}))
        self.logger = (
            dependencies.get("logger")
            if "logger" in dependencies
            else logging.getLogger(__name__)
        )

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="project_standards",
            group="meta",
            description="Aggregates all project standards and sub-validator results.",
            version="v1",
        )

    def get_name(self) -> str:
        return "project_standards"

    def validate(self, target: Path, config: ProjectStandardsValidatorConfig = None):
        self.errors.clear()
        self.warnings.clear()
        self.failed_files.clear()
        is_valid = True
        all_errors = []
        all_warnings = []
        all_suggestions = []
        metadata = {}
        aggregated = []
        for sub_name in self.config.sub_validators:
            validator_cls = self.SUB_VALIDATOR_MAP.get(sub_name)
            if not validator_cls:
                self.add_warning(
                    message=f"Unknown sub-validator: {sub_name}",
                    file="",
                    type="warning",
                )
                continue
            if sub_name == "dockerfile":
                sub_path = target / "Dockerfile"
            elif sub_name == "compose":
                sub_path = target / "docker-compose.yml"
            else:
                sub_path = self.config.paths.get(sub_name, target)
            validator = validator_cls()
            result = validator.validate(Path(sub_path))
            # Patch: handle bool return type for legacy sub-validators
            if isinstance(result, bool):
                result = ValidationResult(
                    is_valid=result, errors=[], warnings=[], version="v1"
                )

            # Aggregate errors/warnings/suggestions with severity if available
            def _format(msg, sev=None, sug=None):
                base = f"[{sub_name}] {msg}"
                if sev:
                    base += f" (severity: {sev})"
                if sug:
                    base += f"\n  Suggestion: {sug}"
                return base

            # Errors
            for err in getattr(result, "errors", []):
                sev = getattr(result, "severity", None)
                sug = getattr(result, "suggestions", None)
                # If err is a string, wrap as ValidationIssue
                if isinstance(err, ValidationIssue):
                    all_errors.append(_format(err.message, sev, sug))
                    aggregated.append(
                        {
                            "validator": sub_name,
                            "type": "error",
                            "message": err.message,
                            "severity": sev,
                            "suggestion": sug,
                        }
                    )
                    self.add_error(
                        message=err.message,
                        file=err.file or "",
                        line=err.line,
                        details=err.details,
                        type="error",
                    )
                else:
                    all_errors.append(_format(str(err), sev, sug))
                    aggregated.append(
                        {
                            "validator": sub_name,
                            "type": "error",
                            "message": str(err),
                            "severity": sev,
                            "suggestion": sug,
                        }
                    )
                    self.add_error(message=str(err), file="", type="error")
                is_valid = False
            # Warnings
            for warn in getattr(result, "warnings", []):
                sev = getattr(result, "severity", None)
                sug = getattr(result, "suggestions", None)
                if isinstance(warn, ValidationIssue):
                    all_warnings.append(_format(warn.message, sev, sug))
                    aggregated.append(
                        {
                            "validator": sub_name,
                            "type": "warning",
                            "message": warn.message,
                            "severity": sev,
                            "suggestion": sug,
                        }
                    )
                    self.add_warning(
                        message=warn.message,
                        file=warn.file or "",
                        line=warn.line,
                        details=warn.details,
                        type="warning",
                    )
                else:
                    all_warnings.append(_format(str(warn), sev, sug))
                    aggregated.append(
                        {
                            "validator": sub_name,
                            "type": "warning",
                            "message": str(warn),
                            "severity": sev,
                            "suggestion": sug,
                        }
                    )
                    self.add_warning(message=str(warn), file="", type="warning")
            # Suggestions (if present)
            for sug in (
                getattr(result, "suggestions", [])
                if hasattr(result, "suggestions")
                else []
            ):
                all_suggestions.append(f"[{sub_name}] {sug}")
            metadata[sub_name] = getattr(result, "metadata", None)
            # Aggregate failed_files if present
            failed_files = getattr(result, "failed_files", None)
            if failed_files:
                for f in failed_files:
                    self.add_failed_file(f)
        # Unified result with extensibility for future consumers
        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            version="v1",
            metadata=metadata,
            aggregated=aggregated,
        )

    def _validate(self, target: Path) -> bool:
        result = self.validate(target)
        return result.is_valid


def check_containers():
    """Validate all containers using the modular validators."""
    logger.info("Validating containers..")
    all_valid = True
    container_dirs = [p for p in Path("./containers").glob("*") if p.is_dir()]

    for container_dir in container_dirs:
        # Structural validation
        structure_errors = validate_container_structure(container_dir)
        if structure_errors:
            all_valid = False
            logger.error(f"Container structure validation errors in {container_dir}:")
            for error in structure_errors:
                logger.error(f"  - {error}")

        # Poetry validation
        poetry_errors = validate_poetry_config(container_dir)
        if poetry_errors:
            all_valid = False
            logger.error(f"Poetry configuration errors in {container_dir}:")
            for error in poetry_errors:
                logger.error(f"  - {error}")

        # Dockerfile validation if file exists
        dockerfile_path = container_dir / "Dockerfile"
        if dockerfile_path.exists():
            dockerfile_errors, dockerfile_warnings = validate_dockerfile(
                dockerfile_path
            )
            if dockerfile_errors:
                all_valid = False
                logger.error(f"Dockerfile validation errors in {dockerfile_path}:")
                for error in dockerfile_errors:
                    logger.error(f"  - {error}")
            if dockerfile_warnings:
                logger.warning(f"Dockerfile validation warnings in {dockerfile_path}:")
                for warning in dockerfile_warnings:
                    logger.warning(f"  - Warning: {warning}")

    # Validate compose file
    compose_path = Path("./docker-compose.yml")
    if compose_path.exists():
        compose_errors = validate_compose_file(str(compose_path))
        if compose_errors:
            all_valid = False
            logger.error("Docker Compose validation errors:")
            for error in compose_errors:
                logger.error(f"  - {error}")

    return all_valid


def check_python_files(directory: str = ".") -> bool:
    """Validate Python files in the specified directory.

    Args:
        directory: Directory to check

    Returns:
        True if all files are valid, False otherwise
    """
    logger.info(f"Validating Python files in {directory}..")
    all_valid = True
    python_files = list(Path(directory).glob("**/*.py"))

    for py_file in python_files:
        valid, errors = validate_python_file(str(py_file))
        if not valid:
            all_valid = False
            logger.error(f"Python validation errors in {py_file}:")
            for error in errors:
                logger.error(f"  - {error}")

    return all_valid


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate project standards (aggregated)"
    )
    parser.add_argument(
        "path", type=str, nargs="?", default=".", help="Path to project root"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    exit_code = 0

    # Determine what to check
    check_all = args.all or (not args.containers and not args.python)

    # Check containers if requested
    if args.containers or check_all:
        containers_valid = check_containers()
        if not containers_valid:
            exit_code = 1

    # Check Python files if requested
    if args.python or check_all:
        python_path = args.path or "."
        python_valid = check_python_files(python_path)
        if not python_valid:
            exit_code = 1

    sys.exit(exit_code)
