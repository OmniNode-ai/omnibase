# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_api
# namespace: omninode.tools.validate_api
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:59+00:00
# last_modified_at: 2025-04-27T18:12:59+00:00
# entrypoint: validate_api.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_api.py
containers.foundation.src.foundation.script.validate.validate_api.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import logging
from pathlib import Path
from typing import Dict, List

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    APISpecValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from foundation.protocol.apispec_loader import APISpecLoader
from foundation.protocol.filesystem import FileSystem
from foundation.protocol.http_client import HTTPClient
from pydantic import Field


class APIValidatorConfig(ValidatorConfig):
    version: str = "v1"
    required_methods: list = Field(default_factory=list)
    require_version: bool = True
    require_documentation: bool = True
    max_response_time: int = 1000


class APIValidator(ProtocolValidate):
    """Validates API endpoints and documentation."""

    def __init__(
        self,
        config=None,
        *,
        spec_loader: APISpecLoader = None,
        http_client: HTTPClient = None,
        filesystem: FileSystem = None,
        **dependencies,
    ):
        super().__init__(config, **dependencies)
        self.config = APIValidatorConfig(**(config or {}))
        self.logger = (
            dependencies.get("logger")
            if "logger" in dependencies
            else logging.getLogger(__name__)
        )
        self.spec_loader = spec_loader
        self.http_client = http_client
        self.filesystem = filesystem

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="api",
            group="quality",
            description="Validates API endpoints and documentation.",
            version="v1",
        )

    def get_name(self) -> str:
        """Get the validator name."""
        return "api"

    def validate(
        self, target: Path, config: APIValidatorConfig = None
    ) -> ValidationResult:
        """Validate API configuration and documentation.

        Args:
            target: Path to API directory
        Returns:
            ValidationResult: Result of the validation
        """
        self.errors.clear()
        self.warnings.clear()
        is_valid = True
        # Look for OpenAPI/Swagger spec
        spec_paths = [
            target / "openapi.yaml",
            target / "openapi.yml",
            target / "openapi.json",
            target / "swagger.yaml",
            target / "swagger.yml",
            target / "swagger.json",
        ]
        spec_file = next((p for p in spec_paths if self.filesystem.exists(p)), None)
        if not spec_file:
            self.errors.append(
                APISpecValidationIssue(
                    message="No OpenAPI/Swagger specification found",
                    file=str(target),
                    type="error",
                )
            )
            return ValidationResult(
                is_valid=False,
                errors=self.errors,
                warnings=self.warnings,
                version=self.config.version,
            )
        try:
            spec = self.spec_loader.load_spec(spec_file)
        except Exception as e:
            self.errors.append(
                APISpecValidationIssue(
                    message=f"Failed to parse API specification: {e}",
                    file=str(spec_file),
                    type="error",
                )
            )
            return ValidationResult(
                is_valid=False,
                errors=self.errors,
                warnings=self.warnings,
                version=self.config.version,
            )
        if spec is None:
            self.errors.append(
                APISpecValidationIssue(
                    message="API specification file is empty or invalid",
                    file=str(spec_file),
                    type="error",
                )
            )
            return ValidationResult(
                is_valid=False,
                errors=self.errors,
                warnings=self.warnings,
                version=self.config.version,
            )
        # Get rules from config
        rules = self.config.model_dump() if hasattr(self.config, "model_dump") else {}
        required_methods = rules.get("required_methods", [])
        require_version = rules.get("require_version", True)
        require_documentation = rules.get("require_documentation", True)
        max_response_time = rules.get("max_response_time", 1000)
        # Validate API version
        if require_version:
            is_valid &= self._validate_version(spec)
        # Validate required methods
        is_valid &= self._validate_methods(spec, required_methods)
        # Validate documentation
        if require_documentation:
            is_valid &= self._validate_documentation(spec)
        # Validate response times if endpoints are provided
        base_url = spec.get("servers", [{}])[0].get("url")
        if base_url:
            is_valid &= self._validate_response_times(spec, base_url, max_response_time)
        # If any warnings, fail validation
        if self.warnings:
            is_valid = False
        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            version=self.config.version,
        )

    def _validate_version(self, spec: Dict) -> bool:
        """Validate API version is specified."""
        if not spec.get("info", {}).get("version"):
            self.errors.append(
                APISpecValidationIssue(
                    message="API version not specified", type="error"
                )
            )
            return False
        return True

    def _validate_methods(self, spec: Dict, required_methods: List[str]) -> bool:
        """Validate required HTTP methods are supported."""
        is_valid = True

        # Get all paths and their methods
        paths = spec.get("paths", {})
        for path, operations in paths.items():
            available_methods = {m.upper() for m in operations.keys()}

            # Check each required method
            for method in required_methods:
                if method.upper() not in available_methods:
                    self.errors.append(
                        APISpecValidationIssue(
                            message=f"Required method {method} not found for path {path}",
                            details={
                                "path": path,
                                "method": method,
                                "available": list(available_methods),
                            },
                            file=str(path),
                            type="error",
                        )
                    )
                    is_valid = False

        return is_valid

    def _validate_documentation(self, spec: Dict) -> bool:
        """Validate API documentation completeness."""
        is_valid = True

        # Check info section
        info = spec.get("info", {})
        if not info.get("title"):
            self.warnings.append(
                APISpecValidationIssue(
                    message="API title not specified", type="warning"
                )
            )
            is_valid = False
        if not info.get("description"):
            self.warnings.append(
                APISpecValidationIssue(
                    message="API description not specified", type="warning"
                )
            )

        # Check paths documentation
        paths = spec.get("paths", {})
        for path, operations in paths.items():
            for method, operation in operations.items():
                if not operation.get("summary"):
                    self.warnings.append(
                        APISpecValidationIssue(
                            message=f"Operation summary missing for {method.upper()} {path}",
                            file=str(path),
                            type="warning",
                        )
                    )
                if not operation.get("description"):
                    self.warnings.append(
                        APISpecValidationIssue(
                            message=f"Operation description missing for {method.upper()} {path}",
                            file=str(path),
                            type="warning",
                        )
                    )

                # Check parameters documentation
                for param in operation.get("parameters", []):
                    if not param.get("description"):
                        self.warnings.append(
                            APISpecValidationIssue(
                                message=f"Parameter description missing for {param.get('name')} "
                                f"in {method.upper()} {path}",
                                file=str(path),
                                type="warning",
                            )
                        )

        return is_valid

    def _validate_response_times(
        self, spec: Dict, base_url: str, max_time: int
    ) -> bool:
        """Validate API response times."""
        is_valid = True
        paths = spec.get("paths", {})
        for path, operations in paths.items():
            if "get" in operations:
                url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
                try:
                    response = self.http_client.get(url, timeout=max_time / 1000)
                    time_ms = response.elapsed_ms
                    if time_ms > max_time:
                        self.warnings.append(
                            APISpecValidationIssue(
                                message=f"Slow response from {path}: {time_ms:.0f}ms (max {max_time}ms)",
                                details={
                                    "path": path,
                                    "response_time": time_ms,
                                    "max_time": max_time,
                                },
                                file=str(path),
                                type="warning",
                            )
                        )
                        is_valid = False
                except Exception as e:
                    self.warnings.append(
                        APISpecValidationIssue(
                            message=f"Failed to test response time for {path}: {e}",
                            details={"path": path},
                            file=str(path),
                            type="warning",
                        )
                    )
                    is_valid = False
        return is_valid

    def _validate(self, target: Path) -> bool:
        result = self.validate(target)
        return result.is_valid
