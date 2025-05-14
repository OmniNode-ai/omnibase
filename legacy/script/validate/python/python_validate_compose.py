#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_compose
# namespace: omninode.tools.validate_compose
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:00+00:00
# last_modified_at: 2025-04-27T18:13:00+00:00
# entrypoint: validate_compose.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_compose.py
containers.foundation.src.foundation.script.validate.validate_compose.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from foundation.protocol.protocol_tool import ProtocolTool
from foundation.script.validate.validate_registry import ValidatorRegistry


class ComposeValidatorConfig(ValidatorConfig):
    version: str = "1.0.0"
    required_service_keys: List[str] = [
        "build",
        "environment",
        "volumes",
        "healthcheck",
    ]
    required_env_vars: List[str] = ["PYTHONPATH", "ENV"]
    required_networks: List[str] = ["platform-net"]
    template_path: Optional[str] = None  # Optionally enforce a template


class ComposeValidationResult(ValidationResult):
    pass


class ComposeValidator(ProtocolValidate, ProtocolTool):
    """Validator for Docker Compose files. Implements ProtocolTool."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.config = ComposeValidatorConfig(**(config or {}))

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="compose",
            group="container",
            description="Validates docker-compose.yml for platform compliance.",
        )

    def validate(
        self, target: Path, config: Optional[ValidatorConfig] = None
    ) -> ComposeValidationResult:
        result = ComposeValidationResult(is_valid=True, errors=[], warnings=[])
        try:
            if not target.is_file():
                result.errors.append(
                    ValidationIssue(
                        message=f"docker-compose.yml not found: {target}",
                        file=str(target),
                        type="error",
                    )
                )
                result.is_valid = False
                return result
            with open(target) as f:
                compose_config = yaml.safe_load(f)
            if not compose_config or "services" not in compose_config:
                result.errors.append(
                    ValidationIssue(
                        message="Invalid docker-compose.yml format: missing 'services'",
                        file=str(target),
                        type="error",
                    )
                )
                result.is_valid = False
                return result
            # Check networks
            result.errors.extend(self.check_networks(compose_config, str(target)))
            # Check dependencies
            result.errors.extend(self.check_dependencies(compose_config, str(target)))
            # Check each service
            for service_name, config in compose_config["services"].items():
                result.errors.extend(
                    self.check_service_config(service_name, config, str(target))
                )
                # Best-practice warnings
                result.warnings.extend(
                    self.check_service_warnings(service_name, config, str(target))
                )
            if result.errors:
                result.is_valid = False
        except Exception as e:
            result.errors.append(
                ValidationIssue(
                    message=f"Validation failed: {str(e)}",
                    file=str(target),
                    type="error",
                )
            )
            result.is_valid = False
        return result

    def check_service_config(
        self, service_name: str, config: Dict, target_file: str
    ) -> List[ValidationIssue]:
        errors = []
        # Required top-level keys
        for key in self.config.required_service_keys:
            if key not in config:
                errors.append(
                    ValidationIssue(
                        message=f"Service '{service_name}' is missing required key: {key}",
                        file=target_file,
                        type="error",
                    )
                )
        # Check environment variables
        if "environment" in config:
            env_vars = set()
            for env in config["environment"]:
                if isinstance(env, str):
                    env_vars.add(env.split("=")[0])
                elif isinstance(env, dict):
                    env_vars.update(env.keys())
            for var in self.config.required_env_vars:
                if var not in env_vars:
                    errors.append(
                        ValidationIssue(
                            message=f"Service '{service_name}' is missing required environment variable: {var}",
                            file=target_file,
                            type="error",
                        )
                    )
        # Check build configuration
        if "build" in config:
            if "context" not in config["build"]:
                errors.append(
                    ValidationIssue(
                        message=f"Service '{service_name}' build is missing context",
                        file=str(target),
                        type="error",
                    )
                )
            if "dockerfile" not in config["build"]:
                errors.append(
                    ValidationIssue(
                        message=f"Service '{service_name}' build is missing dockerfile path",
                        file=str(target),
                        type="error",
                    )
                )
        # Check volumes
        if "volumes" in config:
            source_mounted = any("/app" in volume for volume in config["volumes"])
            if not source_mounted:
                errors.append(
                    ValidationIssue(
                        message=f"Service '{service_name}' must mount source code to /app",
                        file=str(target),
                        type="error",
                    )
                )
        # Check healthcheck
        if "healthcheck" in config:
            required_health_keys = {"test", "interval", "timeout", "retries"}
            health_config = config["healthcheck"]
            for key in required_health_keys:
                if key not in health_config:
                    errors.append(
                        ValidationIssue(
                            message=f"Service '{service_name}' healthcheck is missing: {key}",
                            file=str(target),
                            type="error",
                        )
                    )
        return errors

    def check_service_warnings(
        self, service_name: str, config: Dict, target: Path
    ) -> List[ValidationIssue]:
        warnings = []
        # Warn if no resource limits
        if "deploy" not in config or "resources" not in config.get("deploy", {}):
            warnings.append(
                ValidationIssue(
                    message=f"Service '{service_name}' does not specify resource limits (deploy.resources)",
                    file=str(target),
                    type="warning",
                )
            )
        # Warn if privileged: true
        if config.get("privileged", False):
            warnings.append(
                ValidationIssue(
                    message=f"Service '{service_name}' uses privileged: true (security risk)",
                    file=str(target),
                    type="warning",
                )
            )
        # Warn if restart policy is not always
        if config.get("restart") not in ("always", "unless-stopped"):
            warnings.append(
                ValidationIssue(
                    message=f"Service '{service_name}' does not set restart: always or unless-stopped (recommended for production)",
                    file=str(target),
                    type="warning",
                )
            )
        # Warn if build context is not relative
        if "build" in config and isinstance(config["build"], dict):
            context = config["build"].get("context")
            if context and (
                context.startswith("/")
                or context.startswith("C:\\")
                or context.startswith("D:\\")
            ):
                warnings.append(
                    ValidationIssue(
                        message=f"Service '{service_name}' build.context is not relative (should be relative path)",
                        file=str(target),
                        type="warning",
                    )
                )
        # Warn if depends_on is not using healthcheck
        if "depends_on" in config:
            deps = config["depends_on"]
            if isinstance(deps, list):
                warnings.append(
                    ValidationIssue(
                        message=f"Service '{service_name}' depends_on should use healthcheck conditions (dict form)",
                        file=str(target),
                        type="warning",
                    )
                )
        # Warn if multiple networks
        if (
            "networks" in config
            and isinstance(config["networks"], list)
            and len(config["networks"]) > 1
        ):
            warnings.append(
                ValidationIssue(
                    message=f"Service '{service_name}' is attached to multiple networks (review if necessary)",
                    file=str(target),
                    type="warning",
                )
            )
        # Warn if volumes mount host paths
        if "volumes" in config:
            for volume in config["volumes"]:
                if isinstance(volume, str) and volume.split(":")[0].startswith("/"):
                    warnings.append(
                        ValidationIssue(
                            message=f"Service '{service_name}' volume '{volume}' mounts a host path (potential security risk)",
                            file=str(target),
                            type="warning",
                        )
                    )
        return warnings

    def check_networks(
        self, compose_config: Dict, target: Path
    ) -> List[ValidationIssue]:
        errors = []
        if "networks" not in compose_config:
            errors.append(
                ValidationIssue(
                    message="Missing top-level networks configuration",
                    file=str(target),
                    type="error",
                )
            )
            return errors
        defined_networks = set(compose_config["networks"].keys())
        for network in self.config.required_networks:
            if network not in defined_networks:
                errors.append(
                    ValidationIssue(
                        message=f"Missing required network: {network}",
                        file=str(target),
                        type="error",
                    )
                )
        return errors

    def check_dependencies(
        self, compose_config: Dict, target: Path
    ) -> List[ValidationIssue]:
        errors = []
        for service_name, config in compose_config.get("services", {}).items():
            if "depends_on" in config:
                deps = config["depends_on"]
                if isinstance(deps, dict):
                    for dep, dep_config in deps.items():
                        if "condition" not in dep_config:
                            errors.append(
                                ValidationIssue(
                                    message=f"Service '{service_name}' dependency on '{dep}' should specify a condition",
                                    file=str(target),
                                    type="error",
                                )
                            )
                elif isinstance(deps, list):
                    errors.append(
                        ValidationIssue(
                            message=f"Service '{service_name}' should use healthcheck conditions in depends_on",
                            file=str(target),
                            type="error",
                        )
                    )
        return errors

    def get_name(self) -> str:
        return "compose"

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for ComposeValidator."
        )

    def add_arguments(self) -> None:
        """Add CLI arguments to the parser (if used as a CLI tool)."""
        pass

    def run(self, dry_run: bool = False) -> ValidationResult:
        """Run the validator, supporting dry-run mode."""
        import logging

        logger = logging.getLogger(__name__)
        if dry_run:
            logger.info(
                "[DRY RUN] ComposeValidator would validate Docker Compose files."
            )
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        logger.info("Running ComposeValidator.")
        # Example: validate current directory
        return self.validate(target=".")

    def execute(self) -> ValidationResult:
        """Standard entry point for execution."""
        return self.run(dry_run=False)


# Register the validator
ValidatorRegistry().register(
    name="compose",
    version="1.0.0",
    validator_cls=ComposeValidator,
    meta={
        "name": "compose",
        "version": "1.0.0",
        "group": "container",
        "description": "Validates docker-compose.yml for platform compliance.",
    },
)
