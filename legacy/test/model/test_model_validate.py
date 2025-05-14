#!/usr/bin/env python3

# === OmniNode:Test_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_model_validate"
# namespace: "omninode.tests.model_validate"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "foundation-team"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:14+00:00"
# last_modified_at: "2025-05-05T13:00:14+00:00"
# entrypoint: "test_model_validate.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["ProtocolTest"]
# base_class: ["PythonTestProtocolValidate"]
# mock_safe: true
# === /OmniNode:Test_Metadata ===

"""
Tests for model validation using registry-based test cases.
Follows standards: DI, registry, type hints, docstrings, and metadata.
"""

from pathlib import Path
import pytest
from typing import Generator, Any

from foundation.protocol.protocol_test import ProtocolTest
from foundation.template.python.python_test_base_validator import PythonTestProtocolValidate
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.fixture.fixture_registry import FIXTURE_REGISTRY
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedMessageModel, UnifiedStatus

# Canonical test case matrix: (group, case, case_type, expected_status)
TEST_CASES = [
    ("model_validate", "valid_validate_status", "valid", UnifiedStatus.success),
    ("model_validate", "invalid_validate_status", "invalid", UnifiedStatus.error),
]

class TestModelValidate(PythonTestProtocolValidate, ProtocolTest):
    """Test class for model validation, following the canonical test pattern."""

    @pytest.fixture(scope="class")
    def validator(self) -> Generator[Any, None, None]:
        """Get the validator fixture from the registry."""
        fixture = FIXTURE_REGISTRY.get_fixture("model_validate_fixture")
        yield fixture.get_fixture()

    @pytest.mark.parametrize("group, name, case_type, expected_status", TEST_CASES)
    def test_model_validate_registry_driven(
        self,
        group: str,
        name: str,
        case_type: str,
        expected_status: UnifiedStatus,
        validator: Any
    ) -> None:
        """Test model validation using registry-driven test cases.
        
        Args:
            group: The test case group
            name: The test case name
            case_type: The test case type (valid/invalid)
            expected_status: The expected validation status
            validator: The validator fixture
        """
        fname = TEST_CASE_REGISTRY.get_test_case(group, name, case_type)
        result = validator.validate(Path(fname))
        assert result.status == expected_status, f"Expected {expected_status}, got {result.status} for {fname}"
        if expected_status == UnifiedStatus.success:
            assert not result.errors
            assert not result.warnings
        else:
            assert result.errors