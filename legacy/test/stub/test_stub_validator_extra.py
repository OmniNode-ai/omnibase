#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_stub_validator_extra"
# namespace: "omninode.tools.test_stub_validator_extra"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:27+00:00"
# last_modified_at: "2025-05-05T13:00:27+00:00"
# entrypoint: "test_stub_validator_extra.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolValidate']
# base_class: ['ProtocolValidate']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""validator.py containers.foundation.src.foundation.script.validation.test_st
ubs.validator.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

from typing import Any, Dict, Optional

from foundation.base.base_validator_abc import ProtocolValidate
from foundation.script.validation.models import ValidationResult, ValidatorMetadata
from foundation.script.validation.validator_registry import register_validator

from .config import TestStubScannerConfig
from .scanner import TestStubScanner


@register_validator(
    name="test_stub_scanner",
    version="v1",
    group="quality",
    description="Scans test files for excessive stubbing and non-existent mocks.",
)
class TestStubScannerValidator(ProtocolValidate):
    def __init__(self, config: Optional[Dict[str, Any]] = None, **dependencies):
        super().__init__(config, **dependencies)

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="test_stub_scanner",
            version="v1",
            group="quality",
            description="Scans test files for excessive stubbing and non-existent mocks.",
        )

    def get_name(self) -> str:
        return "test_stub_scanner"

    def validate(
        self, target, config: Optional[TestStubScannerConfig] = None
    ) -> ValidationResult:
        scanner = TestStubScanner(target)
        issues = scanner.scan()
        return ValidationResult(passed=len(issues) == 0, issues=issues)