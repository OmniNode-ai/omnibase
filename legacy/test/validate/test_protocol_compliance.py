# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_protocol_compliance"
# namespace: "foundation.test.validate.test_protocol_compliance"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "foundation-team"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:30:00+00:00"
# last_modified_at: "2025-05-07T12:30:00+00:00"
# entrypoint: "test_protocol_compliance.py"
# protocols_supported:
#   - "O.N.E. v0.1"
# protocol_class:
#   - 'ProtocolTestableCLI'
# base_class:
#   - 'ProtocolTestableCLI'
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Tests for the protocol compliance validator.
Validates that the validator correctly identifies protocol compliance issues.
"""

import ast
import pytest
from pathlib import Path
from typing import List, Set, Dict
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.fixture.fixture_registry import FIXTURE_REGISTRY
from foundation.protocol.protocol_testable_cli import ProtocolTestableCLI
from foundation.model.model_validate import ValidateStatus
from foundation.script.validate.python.python_validate_protocol_compliance import (
    ProtocolComplianceValidator,
    find_protocol_imports,
    find_protocol_implementations,
    get_method_args,
    check_method_compliance,
    check_class_compliance
)

class TestableProtocolCLI:
    """Concrete implementation of ProtocolTestableCLI for testing."""
    
    def run(self, args: List[str] = None) -> int:
        """Run the CLI with the given arguments."""
        return 0

    def get_name(self) -> str:
        """Get the name of the CLI."""
        return "test_protocol_cli"

class TestProtocolComplianceValidator:
    """Test suite for protocol compliance validator."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.validator = ProtocolComplianceValidator()
    
    @pytest.fixture
    def valid_protocol_file(self, tmp_path) -> Path:
        """Create a valid protocol implementation file."""
        content = """
from foundation.protocol import ProtocolValidateMetadataBlock

class ValidValidator(ProtocolValidateMetadataBlock):
    def validate(self, target, config=None):
        pass
    
    def get_name(self):
        return "valid_validator"
"""
        file_path = tmp_path / "valid_validator.py"
        file_path.write_text(content)
        return file_path

    @pytest.fixture
    def invalid_protocol_file(self, tmp_path) -> Path:
        """Create an invalid protocol implementation file."""
        content = """
class InvalidValidator(ProtocolValidateMetadataBlock):
    def validate(self, target, config=None):
        pass
"""
        file_path = tmp_path / "invalid_validator.py"
        file_path.write_text(content)
        return file_path

    @pytest.fixture
    def multiple_protocols_file(self, tmp_path) -> Path:
        """Create a file implementing multiple protocols."""
        content = """
from foundation.protocol import ProtocolValidateMetadataBlock, ProtocolCLI

class MultiProtocolValidator(ProtocolValidateMetadataBlock, ProtocolCLI):
    def validate(self, target, config=None):
        pass
    
    def get_name(self):
        return "multi_validator"
    
    def run(self):
        pass
"""
        file_path = tmp_path / "multi_validator.py"
        file_path.write_text(content)
        return file_path

    @pytest.fixture
    def invalid_method_args_file(self, tmp_path) -> Path:
        """Create a file with invalid method arguments."""
        content = """
from foundation.protocol import ProtocolValidateMetadataBlock

class InvalidArgsValidator(ProtocolValidateMetadataBlock):
    def validate(self, target):  # Missing optional config
        pass
    
    def get_name(self):
        return "invalid_args_validator"
"""
        file_path = tmp_path / "invalid_args_validator.py"
        file_path.write_text(content)
        return file_path
    
    def test_find_protocol_imports(self):
        """Test finding protocol imports in AST."""
        code = """
from foundation.protocol import ProtocolValidateMetadataBlock
import other_module
from foundation.protocol import ProtocolCLI
"""
        tree = ast.parse(code)
        protocols = find_protocol_imports(tree)
        assert "ProtocolValidateMetadataBlock" in protocols
        assert "ProtocolCLI" in protocols
        assert len(protocols) == 2

    def test_find_protocol_implementations(self):
        """Test finding protocol implementations in AST."""
        code = """
class MyValidator(ProtocolValidateMetadataBlock):
    pass

class OtherClass:
    pass
"""
        tree = ast.parse(code)
        implementations = find_protocol_implementations(tree)
        assert "MyValidator" in implementations
        assert "ProtocolValidateMetadataBlock" in implementations["MyValidator"]
        assert "OtherClass" not in implementations

    def test_get_method_args(self):
        """Test getting method arguments and their optional status."""
        code = """
def test_method(required, optional=None, *, kwonly=1):
    pass
"""
        tree = ast.parse(code)
        method_def = tree.body[0]
        args = get_method_args(method_def)
        assert args == {
            'required': False,
            'optional': True,
            'kwonly': True
        }

    def test_check_method_compliance(self):
        """Test method compliance checking."""
        code = """
def validate(target, config=None):
    pass
"""
        tree = ast.parse(code)
        method_def = tree.body[0]
        required_args = {'target': False, 'config': True}
        errors = check_method_compliance(method_def, required_args)
        assert not errors

    def test_check_method_compliance_missing_required(self):
        """Test method compliance checking with missing required argument."""
        code = """
def validate(config=None):
    pass
"""
        tree = ast.parse(code)
        method_def = tree.body[0]
        required_args = {'target': False, 'config': True}
        errors = check_method_compliance(method_def, required_args)
        assert any("Missing required argument 'target'" in error for error in errors)

    def test_check_method_compliance_wrong_optional(self):
        """Test method compliance checking with wrong optional status."""
        code = """
def validate(config, target=None):
    pass
"""
        tree = ast.parse(code)
        method_def = tree.body[0]
        required_args = {'target': False, 'config': True}
        errors = check_method_compliance(method_def, required_args)
        assert any("Argument 'target' should be required" in error for error in errors)
        assert any("Argument 'config' should be optional" in error for error in errors)

    def test_validate_valid(self, valid_protocol_file):
        """Test validation with valid implementation."""
        result = self.validator.validate(str(valid_protocol_file))
        assert result.status == ValidateStatus.VALID

    def test_validate_invalid(self, invalid_protocol_file):
        """Test validation with invalid implementation."""
        result = self.validator.validate(str(invalid_protocol_file))
        assert result.status == ValidateStatus.INVALID

    def test_validate_multiple(self, multiple_protocols_file):
        """Test validation with multiple protocol implementations."""
        result = self.validator.validate(str(multiple_protocols_file))
        assert result.status == ValidateStatus.VALID

    def test_validate_invalid_args(self, invalid_method_args_file):
        """Test validation with invalid method arguments."""
        result = self.validator.validate(str(invalid_method_args_file))
        assert result.status == ValidateStatus.INVALID

    def test_validate_invalid_file(self, tmp_path):
        """Test validation with invalid Python file."""
        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text("this is not valid python code")
        result = self.validator.validate(str(invalid_file))
        assert result.status == ValidateStatus.INVALID

if __name__ == '__main__':
    pytest.main([__file__]) 