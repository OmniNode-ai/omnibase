#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_stub_validator"
# namespace: "omninode.tools.test_stub_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:27+00:00"
# last_modified_at: "2025-05-05T13:00:27+00:00"
# entrypoint: "test_stub_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolValidate', 'ValidatorConfig']
# base_class: ['ProtocolValidate', 'ValidatorConfig']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""test_stub_validator.py containers.foundation.src.foundation.script.validati
on.test_stub.test_stub_validator.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[6] / "src"))

from typing import Any, Dict, Optional

from foundation.base.base_validator_abc import ProtocolValidate
from foundation.base.model_base import (
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from foundation.script.validation.validator_registry import register_validator
from pydantic import Field

from .test_stub_scanner import TestStubScanner


class TestStubScannerConfig(ValidatorConfig):
    __test__ = False
    version: str = "v1"
    mock_ratio_threshold: float = Field(
        default=0.5, description="Max allowed ratio of mocks to assertions"
    )
    mock_absolute_threshold: int = Field(
        default=5, description="Max allowed number of mocks per test"
    )
    patch_threshold: int = Field(
        default=3, description="Max allowed number of patches per test"
    )
    verbose: bool = False
    staged_only: bool = False


@register_validator(
    name="test_stub_scanner",
    version="v1",
    group="quality",
    description="Scans test files for excessive stubbing and non-existent mocks.",
)
class TestStubScannerValidator(ProtocolValidate):
    """Validator wrapper for TestStubScanner utility."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = TestStubScannerConfig(**(config or {}))

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="test_stub_scanner",
            group="quality",
            description="Scans test files for excessive stubbing and non-existent mocks.",
            version="v1",
        )

    def get_name(self) -> str:
        return "test_stub_scanner"

    def validate(
        self, target, config: Optional[TestStubScannerConfig] = None
    ) -> ValidationResult:
        cfg = config or self.config
        scanner = TestStubScanner(
            path=str(target),
            mock_ratio_threshold=cfg.mock_ratio_threshold,
            mock_absolute_threshold=cfg.mock_absolute_threshold,
            patch_threshold=cfg.patch_threshold,
            verbose=cfg.verbose,
            staged_only=cfg.staged_only,
        )
        issues = scanner.scan()
        errors = [str(issue) for issue in issues if issue.get("severity") == "HIGH"]
        warnings = [str(issue) for issue in issues if issue.get("severity") == "MEDIUM"]
        is_valid = not errors
        return ValidationResult(
            is_valid=is_valid, errors=errors, warnings=warnings, version=cfg.version
        )