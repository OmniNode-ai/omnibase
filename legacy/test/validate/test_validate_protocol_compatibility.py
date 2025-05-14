#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_protocol_compatibility"
# namespace: "omninode.tools.test_validate_protocol_compatibility"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00+00:00"
# last_modified_at: "2025-05-07T12:00:00+00:00"
# entrypoint: "test_validate_protocol_compatibility.py"
# protocols_supported:
#   - "["O.N.E. v0.1"]"
# protocol_class:
#   - '['PythonTestProtocolValidate']'
# base_class:
#   - '['PythonTestProtocolValidate']'
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Test suite for protocol compatibility validation.

This module provides comprehensive tests for protocol compatibility validation, including:
- Protocol compliance
- Type safety
- Runtime protocol checking
- Registry integration
- Version compatibility validation
"""

import pytest
from typing import Any, Dict, Optional
from pathlib import Path
import json

from foundation.script.validate.python.python_validate_protocol_compatibility import PythonValidateProtocolCompatibility
from foundation.script.validate.validate_registry import ValidatorRegistry, validate_registry
from foundation.template.python.python_test_base_validator import PythonTestProtocolValidate
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedMessageModel, UnifiedStatus
from foundation.model.model_metadata import MetadataBlockModel

class MockValidator:
    """Mock validator for testing."""
    def validate(self, *args, **kwargs):
        pass

    @classmethod
    def metadata(cls):
        return {
            "name": "mock_validator",
            "version": "1.0.0",
            "protocol_version": "0.1.0"
        }

@pytest.fixture
def utility_registry() -> Dict[str, Any]:
    """Create a utility registry for testing.
    
    Returns:
        Dict[str, Any]: Registry with common utilities
    """
    class Registry(dict):
        def register(self, name: str, obj: Any) -> None:
            self[name] = obj
        def get(self, name: str) -> Any:
            return self[name]
    reg = Registry()
    reg.register('common_error_utils', {
        'create_error': lambda **kwargs: ValidationIssue(**kwargs)
    })
    return reg

@pytest.fixture
def clean_registry():
    """Provide a clean registry for each test."""
    registry = ValidatorRegistry()
    yield registry

class TestPythonValidateProtocolCompatibility(PythonTestProtocolValidate):
    """Test suite for protocol compatibility validation."""
    
    @pytest.fixture(autouse=True)
    def _setup(self, request: Any, utility_registry: Dict[str, Any], clean_registry) -> None:
        """Setup test fixtures."""
        self.validator = PythonValidateProtocolCompatibility(config={}, registry=clean_registry)
    
    def get_tool(self):
        return self.validator
    
    def test_protocol_compliance(self) -> None:
        """Test that validator implements the protocol correctly."""
        assert hasattr(self.validator, 'validate')
        assert hasattr(self.validator, 'get_name')
        assert hasattr(self.validator, 'metadata')
        assert hasattr(self.validator, 'validate_main')
    
    def test_type_safety(self) -> None:
        """Test type safety of validator methods."""
        # Test validate() type safety
        result = self.validator.validate("dummy_path")
        assert isinstance(result, UnifiedResultModel)
        assert isinstance(result.status, UnifiedStatus)
        assert hasattr(result, 'messages')
        assert isinstance(result.messages, list)
        assert all(isinstance(e, UnifiedMessageModel) for e in result.messages)
        
        # Test get_name() type safety
        name = self.validator.get_name()
        assert isinstance(name, str)
        
        # Test metadata() type safety
        meta = self.validator.metadata()
        assert isinstance(meta, MetadataBlockModel)
    
    def test_compatible_validator(self, clean_registry) -> None:
        """Test validation of compatible validator."""
        # Get test case path from registry
        test_case_path = TEST_CASE_REGISTRY.get_test_case("protocol_compatibility", "valid_compatible_validator", "valid")
        assert test_case_path is not None, "Test case not found in registry"
        
        # Register a compatible validator
        clean_registry.register(
            "test_validator",
            MockValidator,
            MockValidator.metadata()
        )
        
        result = self.validator.validate(test_case_path)
        assert result.status == UnifiedStatus.success
        assert not result.messages
    
    def test_incompatible_validator(self, clean_registry) -> None:
        """Test validation of incompatible validator."""
        # Get test case path from registry
        test_case_path = TEST_CASE_REGISTRY.get_test_case("protocol_compatibility", "invalid_incompatible_validator", "invalid")
        assert test_case_path is not None, "Test case not found in registry"
        
        # Register an incompatible validator
        meta = MockValidator.metadata()
        meta["protocol_version"] = "1.0.0"  # Incompatible version
        clean_registry.register(
            "test_validator",
            MockValidator,
            meta
        )
        
        result = self.validator.validate(test_case_path)
        assert result.status == UnifiedStatus.error
        assert len(result.messages) == 1
        assert "incompatible" in result.messages[0].summary.lower()
        
        # Check error details
        error = result.messages[0]
        assert error.context and error.context["validator"] == "protocol_compatibility"
        assert error.file == test_case_path
        assert json.loads(error.details)["validator_name"] == "test_validator"
        assert json.loads(error.details)["validator_version"] == "1.0.0"
        assert json.loads(error.details)["protocol_version"] == "0.1.0"
    
    def test_multiple_versions(self, clean_registry) -> None:
        """Test validation with multiple validator versions."""
        # Get test case path from registry
        test_case_path = TEST_CASE_REGISTRY.get_test_case("protocol_compatibility", "invalid_multiple_versions", "invalid")
        assert test_case_path is not None, "Test case not found in registry"
        
        # Register compatible version
        clean_registry.register(
            "test_validator",
            MockValidator,
            MockValidator.metadata()
        )
        
        # Register incompatible version
        meta = MockValidator.metadata()
        meta["version"] = "2.0.0"
        meta["protocol_version"] = "1.0.0"
        clean_registry.register(
            "test_validator",
            MockValidator,
            meta
        )
        
        result = self.validator.validate(test_case_path)
        assert result.status == UnifiedStatus.error
        assert len(result.messages) == 1
        assert "incompatible" in result.messages[0].summary.lower()
        
        # Check error details
        error = result.messages[0]
        assert error.context and error.context["validator"] == "protocol_compatibility"
        assert error.file == test_case_path
        assert json.loads(error.details)["validator_name"] == "test_validator"
        assert json.loads(error.details)["validator_version"] == "2.0.0"
        assert json.loads(error.details)["protocol_version"] == "0.1.0"
    
    def test_empty_registry(self, clean_registry) -> None:
        """Test validation with empty registry."""
        # Get test case path from registry
        test_case_path = TEST_CASE_REGISTRY.get_test_case("protocol_compatibility", "valid_empty_registry", "valid")
        assert test_case_path is not None, "Test case not found in registry"
        # Ensure registry is empty
        # (No registration step)
        result = self.validator.validate(test_case_path)
        assert result.status == UnifiedStatus.success
        assert not result.messages
    
    def test_validator_metadata(self) -> None:
        """Test validator metadata."""
        meta = self.validator.metadata()
        assert meta.name == "protocol_compatibility"
        assert meta.version == "1.0.0"
        assert meta.protocol_version == "0.1.0"
        assert "protocol" in (meta.tags or [])
        assert "compatibility" in (meta.tags or [])
    
    def test_validation_error_handling(self, clean_registry) -> None:
        """Test error handling during validation."""
        # Get test case path from registry
        test_case_path = TEST_CASE_REGISTRY.get_test_case("protocol_compatibility", "invalid_broken_registry", "invalid")
        assert test_case_path is not None, "Test case not found in registry"
        # Mock list_validators to raise an exception
        import types
        original_list_validators = clean_registry.list_validators
        def raise_exception():
            raise Exception("Simulated registry error")
        clean_registry.list_validators = raise_exception
        try:
            result = self.validator.validate(test_case_path)
            assert result.status == UnifiedStatus.error
            assert len(result.messages) == 1
            assert "Error during protocol compatibility validation" in result.messages[0].summary
        finally:
            clean_registry.list_validators = original_list_validators 