#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_metadata_block"
# namespace: "omninode.tools.test_validate_metadata_block"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T22:11:58+00:00"
# last_modified_at: "2025-05-05T22:11:58+00:00"
# entrypoint: "test_validate_metadata_block.py"
# protocols_supported:
#   - "["O.N.E. v0.1"]"
# protocol_class:
#   - '['PythonTestProtocolValidate']'
# base_class:
#   - '['PythonTestProtocolValidate']'
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Test suite for metadata block validation.

This module provides comprehensive tests for metadata block validation, including:
- Protocol compliance
- Type safety
- Runtime protocol checking
- Registry integration
- File format validation
"""

import shutil
import tempfile
from pathlib import Path
import pytest
import yaml
from typing import Any, Dict, List, Optional, Type
from foundation.script.validate.python.python_validate_metadata_block import PythonValidateMetadataBlock
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.template.python.python_test_base_validator import PythonTestProtocolValidate
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedMessageModel, UnifiedStatus
from foundation.script.validate.validate_metadata_block_registry import MetadataValidateBlockRegistry
from foundation.script.validate.common.common_file_utils import FileUtils
from foundation.script.validate.common.common_yaml_utils import YamlUtils
from foundation.script.validate.common.common_error_utils import CommonErrorUtils
from foundation.script.validate.common.common_json_utils import safe_json_dumps
from foundation.protocol.protocol_stubs import ProtocolValidateMetadataBlock as ProtocolStub
from foundation.base.base_metadata_block_test import BaseMetadataBlockTest

REQUIRED_FIELDS = [
    "metadata_version",
    "name",
    "namespace",
    "version",
    "entrypoint",
    "protocols_supported",
    "owner",
]

# Create a global instance for the test module
metadata_validate_block_registry = MetadataValidateBlockRegistry()

@pytest.fixture
def utility_registry() -> Dict[str, Any]:
    """Create a utility registry for testing.
    
    Returns:
        Dict[str, Any]: Registry with file, YAML, and JSON utilities
    """
    class Registry(dict):
        def register(self, name: str, obj: Any) -> None:
            self[name] = obj
        def get(self, name: str) -> Any:
            return self[name]
    reg = Registry()
    reg.register('file_utils', FileUtils())
    reg.register('yaml_utils', YamlUtils())
    reg.register('common_error_utils', CommonErrorUtils())
    reg.register('json_utils', {'safe_json_dumps': safe_json_dumps})
    return reg

class TestValidateMetadataBlock(BaseMetadataBlockTest):
    """Hybrid pattern: Implements ProtocolValidateMetadataBlock interface, but does not inherit from Protocol."""
    def validate(self, target: Path, config: Optional[Dict[str, Any]] = None) -> Any:
        # Example implementation for protocol compliance
        utility_registry = config["utility_registry"] if config and "utility_registry" in config else {}
        validator = self._get_validator_for_file(str(target), utility_registry)
        return validator.validate(target)

    def get_name(self) -> str:
        return "TestValidateMetadataBlock"

    def test_protocol_compliance(self, utility_registry: Dict[str, Any]) -> None:
        for ext in ['.py', '.yaml', '.md']:
            validator_cls = metadata_validate_block_registry.get_validator(ext)
            assert validator_cls is not None, f"No validator registered for {ext}"
            validator = validator_cls(logger=None, utility_registry=utility_registry)
            # Protocol compliance: implements required methods
            assert hasattr(validator, 'validate'), f"{validator_cls.__name__} must implement validate()"
            assert hasattr(validator, 'get_name'), f"{validator_cls.__name__} must implement get_name()"
            assert hasattr(validator, 'validate_main'), f"{validator_cls.__name__} must implement validate_main()"

    def test_metadata_validator_positive(self, utility_registry: Dict[str, Any]) -> None:
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "valid_metadata_positive", "valid")
        validator = self._get_validator_for_file(fname, utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.success
        assert all(m.severity != "error" for m in result.messages)

    def test_metadata_validator_missing_fields(self, utility_registry: Dict[str, Any]) -> None:
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "invalid_metadata_missing_fields", "invalid")
        validator = self._get_validator_for_file(fname, utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.error
        assert any("Metadata block validation error" in m.summary for m in result.messages)
        assert any(m.severity == "error" for m in result.messages)

    def test_metadata_validator_not_dict(self, utility_registry: Dict[str, Any]) -> None:
        """Test validation of non-dictionary metadata."""
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "invalid_metadata_not_dict", "invalid")
        validator = self._get_validator_for_file(fname, utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.error
        assert any("not a mapping" in m.summary or "dict" in m.summary or "Metadata block validation error" in m.summary for m in result.messages)
        assert any(m.severity == "error" for m in result.messages)

    def test_metadata_validator_yaml_error(self, utility_registry: Dict[str, Any]) -> None:
        """Test validation of invalid YAML metadata."""
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "invalid_metadata_yaml_error", "invalid")
        validator = self._get_validator_for_file(fname, utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.error
        assert any("YAML load error" in m.summary for m in result.messages)
        assert any(m.severity == "error" for m in result.messages)

    def test_metadata_validator_valid_files(self, utility_registry: Dict[str, Any]) -> None:
        """Test validation of valid files."""
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "valid_metadata", "valid")
        validator = self._get_validator_for_file(fname, utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.success
        assert all(m.severity != "error" for m in result.messages)

    def test_metadata_validator_invalid_files(self, utility_registry: Dict[str, Any]) -> None:
        """Test validation of invalid files."""
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "invalid_metadata_missing_owner", "invalid")
        validator = self._get_validator_for_file(fname, utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.error
        assert any("Metadata block validation error" in m.summary for m in result.messages)
        assert any(m.severity == "error" for m in result.messages)

class TestPythonValidateMetadataBlockIsolated:
    """Isolated tests for Python metadata block validation."""
    
    def test_valid(self, utility_registry: Dict[str, Any]) -> None:
        """Test validation of valid Python metadata."""
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "valid_metadata_py", "valid")
        ext = Path(fname).suffix.lower()
        validator_cls = metadata_validate_block_registry.get_validator(ext)
        validator = validator_cls(logger=None, utility_registry=utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.success
        assert all(m.severity != "error" for m in result.messages)

    def test_invalid(self, utility_registry: Dict[str, Any]) -> None:
        """Test validation of invalid Python metadata."""
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "invalid_metadata_py_missing_type", "invalid")
        ext = Path(fname).suffix.lower()
        validator_cls = metadata_validate_block_registry.get_validator(ext)
        validator = validator_cls(logger=None, utility_registry=utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.error
        assert any(m.severity == "error" for m in result.messages)

class TestYamlValidateMetadataBlockIsolated:
    """Isolated tests for YAML metadata block validation."""
    
    def test_valid(self, utility_registry: Dict[str, Any]) -> None:
        """Test validation of valid YAML metadata."""
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "valid_metadata_yaml", "valid")
        ext = Path(fname).suffix.lower()
        validator_cls = metadata_validate_block_registry.get_validator(ext)
        validator = validator_cls(logger=None, utility_registry=utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.success
        assert all(m.severity != "error" for m in result.messages)

    def test_invalid(self, utility_registry: Dict[str, Any]) -> None:
        """Test validation of invalid YAML metadata."""
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "invalid_metadata_yaml_missing_type", "invalid")
        ext = Path(fname).suffix.lower()
        validator_cls = metadata_validate_block_registry.get_validator(ext)
        validator = validator_cls(logger=None, utility_registry=utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.error
        assert any(m.severity == "error" for m in result.messages)

class TestMarkdownValidateMetadataBlockIsolated:
    """Isolated tests for Markdown metadata block validation."""
    
    def test_valid(self, utility_registry: Dict[str, Any]) -> None:
        """Test validation of valid Markdown metadata."""
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "valid_metadata_md", "valid")
        ext = Path(fname).suffix.lower()
        validator_cls = metadata_validate_block_registry.get_validator(ext)
        validator = validator_cls(logger=None, utility_registry=utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.success
        assert all(m.severity != "error" for m in result.messages)

    def test_invalid(self, utility_registry: Dict[str, Any]) -> None:
        """Test validation of invalid Markdown metadata."""
        fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "invalid_metadata_md_missing_type", "invalid")
        ext = Path(fname).suffix.lower()
        validator_cls = metadata_validate_block_registry.get_validator(ext)
        validator = validator_cls(logger=None, utility_registry=utility_registry)
        result = validator.validate(Path(fname))
        assert result.status == UnifiedStatus.error
        assert any(m.severity == "error" for m in result.messages)

# Canonical test case matrix: (group, case, case_type, expected_ext, expected_status)
TEST_CASES = [
    ("metadata_block", "valid_metadata_py", "valid", ".py", UnifiedStatus.success),
    ("metadata_block", "invalid_metadata_py_missing_type", "invalid", ".py", UnifiedStatus.error),
    ("metadata_block", "valid_metadata_yaml", "valid", ".yaml", UnifiedStatus.success),
    ("metadata_block", "invalid_metadata_yaml_missing_type", "invalid", ".yaml", UnifiedStatus.error),
    ("metadata_block", "valid_metadata_md", "valid", ".md", UnifiedStatus.success),
    ("metadata_block", "invalid_metadata_md_missing_type", "invalid", ".md", UnifiedStatus.error),
]

@pytest.mark.parametrize("group, name, case_type, expected_ext, expected_status", TEST_CASES)
def test_metadata_block_validators_registry_driven(
    group: str,
    name: str,
    case_type: str,
    expected_ext: str,
    expected_status: UnifiedStatus,
    utility_registry: Dict[str, Any]
) -> None:
    """Test metadata block validators using registry-driven test cases.
    
    Args:
        group: Test case group
        name: Test case name
        case_type: Test case type (valid/invalid)
        expected_ext: Expected file extension
        expected_status: Expected validation status
        utility_registry: Registry of utilities
    """
    fname = TEST_CASE_REGISTRY.get_test_case(group, name, case_type)
    ext = Path(fname).suffix.lower()
    validator_cls = metadata_validate_block_registry.get_validator(ext)
    assert validator_cls is not None, f"No validator registered for {ext}"
    validator = validator_cls(logger=None, utility_registry=utility_registry)
    result = validator.validate(Path(fname))
    assert result.status == expected_status, f"Expected {expected_status}, got {result.status} for {fname}"

@pytest.mark.parametrize("ext", [".py", ".yaml", ".md"])
def test_validator_has_passing_and_failing_case(ext: str, utility_registry: Dict[str, Any]) -> None:
    """Test that each validator has both passing and failing test cases.

    Args:
        ext: File extension to test
        utility_registry: Registry of utilities
    """
    validator_cls = metadata_validate_block_registry.get_validator(ext)
    assert validator_cls is not None, f"No validator registered for {ext}"
    validator = validator_cls(logger=None, utility_registry=utility_registry)

    # Test passing case
    valid_fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "valid_metadata_py" if ext == ".py" else "valid_metadata_yaml" if ext == ".yaml" else "valid_metadata_md", "valid")
    assert valid_fname is not None, f"No valid test case found for {ext}"
    valid_result = validator.validate(Path(valid_fname))
    assert valid_result.status == UnifiedStatus.success
    assert all(m.severity != "error" for m in valid_result.messages)

    # Test failing case
    invalid_fname = TEST_CASE_REGISTRY.get_test_case("metadata_block", "invalid_metadata_py_missing_type" if ext == ".py" else "invalid_metadata_yaml_missing_type" if ext == ".yaml" else "invalid_metadata_md_missing_type", "invalid")
    assert invalid_fname is not None, f"No invalid test case found for {ext}"
    invalid_result = validator.validate(Path(invalid_fname))
    assert invalid_result.status == UnifiedStatus.error
    assert any(m.severity == "error" for m in invalid_result.messages)