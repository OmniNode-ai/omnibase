#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_profile_schema
# namespace: omninode.tools.validate_profile_schema
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:04+00:00
# last_modified_at: 2025-04-27T18:13:04+00:00
# entrypoint: validate_profile_schema.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""
validate_profile_schema.py
Module for validating OmniNode profile YAML schemas using Pydantic models.
Can be used as an importable module or as a CLI tool.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from pydantic import BaseModel, ValidationError
from foundation.model.model_validation_issue_mixin import ValidationIssueMixin


class ProfileSchemaValidatorConfig(ValidatorConfig):
    version: str = "v1"
    # Add config fields if needed


class OmniNodeProfileMetadata(BaseModel):
    metadata_version: str
    name: str
    namespace: str
    version: str
    author: str
    created_by: str
    created_at: str
    last_modified_by: str
    last_updated: str
    changelog: list
    status: str
    description: str
    registry_url: Optional[str] = None
    trust_zones: list
    bundle: bool
    compatibility: dict


class RuleMetadata(BaseModel):
    name: str
    tool: str
    description: str
    enabled: bool
    tags: list
    docs_url: Optional[str] = None
    auto_fix: bool = False
    fix_command: Optional[str] = None
    pattern: Optional[str] = None
    severity: Optional[str] = None
    params: Optional[dict] = None


class OmniNodeValidationProfile(BaseModel):
    metadata: OmniNodeProfileMetadata
    language: str
    extends: Optional[str] = None
    rules: list[RuleMetadata]
    policy: dict
    compliance_requirements: list
    platform_matrix: list
    test_status: str
    coverage: float
    ci_url: Optional[str] = None
    telemetry: dict
    last_updated: str


def load_profile_yaml(path: Path) -> dict:
    """Load a YAML file and return its contents as a dict."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def extract_metadata_block(profile: dict) -> dict:
    """Extract the metadata block from a profile dict."""
    if "metadata" in profile and isinstance(profile["metadata"], dict):
        return profile["metadata"]
    meta_keys = [
        "metadata_version",
        "name",
        "namespace",
        "version",
        "author",
        "created_by",
        "created_at",
        "last_modified_by",
        "last_updated",
        "changelog",
        "status",
        "description",
        "registry_url",
        "trust_zones",
        "bundle",
        "compatibility",
    ]
    return {k: v for k, v in profile.items() if k in meta_keys}


class ProfileSchemaValidator(ValidationIssueMixin, ProtocolValidate):
    """Validates OmniNode profile YAML schemas against the canonical schema."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = ProfileSchemaValidatorConfig(**(config or {}))
        self.errors: list = []
        self.warnings: list = []
        self.failed_files: list = []

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="profile_schema",
            description="Validates OmniNode profile YAML schemas against the canonical schema.",
            version="v1",
        )

    def get_name(self) -> str:
        return "profile_schema"

    def validate(
        self, target: Path, config: Optional[ProfileSchemaValidatorConfig] = None
    ) -> ValidationResult:
        cfg = config or self.config
        errors = []
        warnings: list = []
        suggestions: list = []
        is_valid = True
        try:
            profile = load_profile_yaml(target)
            metadata_dict = extract_metadata_block(profile)
            metadata_obj = OmniNodeProfileMetadata(**metadata_dict)
            profile_dict = {
                "metadata": metadata_obj,
                "language": profile.get("language"),
                "extends": profile.get("extends"),
                "rules": profile.get("rules", []),
                "policy": profile.get("policy", {}),
                "compliance_requirements": profile.get("compliance_requirements", []),
                "platform_matrix": profile.get("platform_matrix", []),
                "test_status": profile.get("test_status", ""),
                "coverage": profile.get("coverage", 0.0),
                "ci_url": profile.get("ci_url"),
                "telemetry": profile.get("telemetry", {}),
                "last_updated": profile.get("last_updated", ""),
            }
            OmniNodeValidationProfile(**profile_dict)
        except ValidationError as e:
            is_valid = False
            errors.append(
                ValidationIssue(message=str(e), file=str(target), type="error")
            )
        except Exception as e:
            is_valid = False
            errors.append(
                ValidationIssue(
                    message=f"Unexpected error: {e}", file=str(target), type="error"
                )
            )
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            version=cfg.version,
        )

    def _validate(self, target: Path) -> bool:
        result = self.validate(target)
        return result.is_valid

    def describe_flags(self):
        """No-op for protocol compliance."""
        return None

    def description(self):
        return None

    def get_parser(self):
        return None

    def validate_main(self):
        return None

    def logger(self):
        return None

    def main(self):
        return None

    def run(self):
        return None


def validate_profile_schema(path: str, verbose: bool = False) -> bool:
    """Validate a profile schema YAML file."""
    errors = []
    warnings: list = []
    try:
        result = ProfileSchemaValidator().validate(Path(path))
        if not result.is_valid:
            if verbose:
                for err in result.errors:
                    print(f"ERROR: {err.message}")
            return False
        return True
    except Exception as e:
        errors.append(
            ValidationIssue(
                message=f"Unexpected error: {e}", file=str(path), type="error"
            )
        )
        if verbose:
            print(f"ERROR: Unexpected error: {e}")
        return False


def main():
    """CLI entrypoint for validating a profile YAML file."""
    import argparse

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
    )
    parser = argparse.ArgumentParser(
        description="Validate an OmniNode profile YAML schema."
    )
    parser.add_argument("profile_yaml", type=str, help="Path to the profile YAML file.")
    parser.add_argument("--verbose", action="store_true", help="Print detailed output.")
    args = parser.parse_args()
    path = Path(args.profile_yaml)
    valid = validate_profile_schema(path, verbose=args.verbose)
    if valid:
        sys.exit(0)
    else:
        sys.exit(2)


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()
