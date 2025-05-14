#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "validate_template_validator"
# namespace: "omninode.tools.validate_template_validator"
# meta_type: "validator"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "validate_template_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolValidate', 'ValidatorConfig']
# base_class: ['ProtocolValidate', 'ValidatorConfig']
# mock_safe: true
# === /OmniNode:Metadata ===




"""
Canonical Foundation Validator Template
Demonstrates all required patterns for maintainable, testable, and registry-driven validators.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import logging

from foundation.base.model_base import ValidationResult, ValidatorConfig, ValidatorMetadata, ValidationIssue
from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.script.validate.validator_registry import register_validator

class ExampleValidatorConfig(ValidatorConfig):
    version: str = "v1"
    example_field: Optional[str] = None

@register_validator(
    name="example_validator",
    version="v1",
    group="example",
    description="Example validator demonstrating all required patterns."
)
class ExampleValidator(ProtocolValidate):
    """Example validator with all required patterns."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = ExampleValidatorConfig(**(config or {}))
        self.logger = dependencies.get("logger") if "logger" in dependencies else logging.getLogger(__name__)

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        """Return validator metadata."""
        return ValidatorMetadata(
            name="example_validator",
            group="example",
            description="Example validator demonstrating all required patterns.",
            version="v1",
        )

    def get_name(self) -> str:
        """Get the validator name."""
        return "example_validator"

    def validate(self, target: Path, config: Optional[ExampleValidatorConfig] = None) -> ValidationResult:
        """Validate the target using all required patterns."""
        self.errors.clear()
        self.warnings.clear()
        is_valid = True
        cfg = config or self.config
        try:
            # Example logic: check if file exists
            if not target.exists():
                self.add_error(
                    message=f"Target not found: {target}",
                    file=str(target),
                    details={"reason": "missing"}
                )
                is_valid = False
            # Example config usage
            if cfg.example_field == "warn":
                self.add_warning(
                    message="Example warning due to config.",
                    file=str(target),
                    details={"config": "example_field=warn"}
                )
        except Exception as e:
            self.add_error(
                message=f"Validation failed: {e}",
                file=str(target),
                details={"exception": str(e)}
            )
            is_valid = False
        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            version=cfg.version
        ) 