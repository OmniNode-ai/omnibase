import pytest
from pathlib import Path
from textwrap import dedent
from typing import List
import argparse
from unittest.mock import patch, MagicMock

from foundation.protocol.protocol_naming_convention import NamingViolation
from foundation.script.validate.validate_naming_convention import (
    NamingConventionValidator,
    RuleBasedNamingCheck,
    main
)
from foundation.fixture.fixture_naming_convention import NamingConventionRules
from foundation.di.di_container import DIContainer
from foundation.bootstrap.bootstrap import bootstrap
from foundation.model.model_unified_result import UnifiedStatus

@pytest.fixture(scope="session", autouse=True)
def setup_di():
    """Set up DI container for all tests."""
    bootstrap()
    container = DIContainer()
    container.register(NamingConventionRules)
    return container

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Valid files
    (tmp_path / "python_validate_test.py").write_text(dedent("""
        class PythonValidateTestClass:
            pass
    """))
    
    (tmp_path / "test_valid.py").write_text(dedent("""
        class PythonTestValidClass:
            pass
    """))
    
    # Invalid files - prefix rule violation
    (tmp_path / "invalid-test.py").write_text(dedent("""
        class InvalidTestClass:
            pass
    """))
    
    # Invalid files - general rule violation
    (tmp_path / "Invalid_Name.py").write_text(dedent("""
        class InvalidClass:
            pass
    """))
    
    # Add a file with read permission issues
    no_read_file = tmp_path / "no_read.py"
    no_read_file.write_text("test")
    no_read_file.chmod(0o000)  # Remove all permissions
    
    return tmp_path

@pytest.fixture
def validator(setup_di, temp_dir):
    """Create a validator with test rules."""
    validator = NamingConventionValidator(config={}, di_container=setup_di)
    return validator

def test_rule_based_naming_check(setup_di, temp_dir):
    """Test the rule-based naming check."""
    naming_rules = setup_di.resolve(NamingConventionRules)
    
    # Test prefix rule
    test_rule = naming_rules.get_rule("test_file_naming")
    check = RuleBasedNamingCheck(test_rule)
    
    # Valid test file
    valid_file = temp_dir / "test_valid.py"
    assert check.validate(valid_file) is None
    
    # Invalid test file
    invalid_file = temp_dir / "invalid-test.py"  # Contains hyphen, should be snake_case
    violation = check.validate(invalid_file)
    assert violation is not None
    assert violation.violation_type == "pattern_violation"
    assert violation.current_name == "invalid-test.py"
    
    # Test general rule
    general_rule = naming_rules.get_rule("general_file_naming")
    check = RuleBasedNamingCheck(general_rule)
    
    # Invalid general file
    invalid_file = temp_dir / "Invalid_Name.py"  # Contains uppercase, should be snake_case
    violation = check.validate(invalid_file)
    assert violation is not None
    assert violation.violation_type == "pattern_violation"
    assert violation.current_name == "Invalid_Name.py"

def test_validator_directory_scan(validator, temp_dir):
    """Test scanning an entire directory."""
    violations = validator.validate_directory(temp_dir)
    
    # Should find violations in both invalid files
    assert len(violations) >= 2  # At least 2 violations (invalid file names)
    
    # Check that violations were found
    file_paths = [v.file_path for v in violations]
    assert str(temp_dir / "invalid-test.py") in file_paths
    assert str(temp_dir / "Invalid_Name.py") in file_paths

def test_validate_result_model(validator, temp_dir):
    """Test the UnifiedResultModel output."""
    result = validator.validate(temp_dir)
    
    assert result.tool_name == "naming_convention"
    assert result.target == str(temp_dir)
    assert result.version.protocol_version == "1.0"
    assert len(result.messages) >= 2  # At least 2 violations
    
    # Check that both violations are reported
    file_paths = [msg.file for msg in result.messages]
    assert str(temp_dir / "invalid-test.py") in file_paths
    assert str(temp_dir / "Invalid_Name.py") in file_paths

def test_report_generation(validator, temp_dir):
    """Test report generation."""
    violations = validator.validate_directory(temp_dir)
    report = validator.generate_report(violations)
    
    # Check report content
    assert "Naming Convention Violations:" in report
    assert "invalid-test.py" in report
    assert "Invalid_Name.py" in report
    assert "pattern_violation" in report

def test_validate_path_error_handling(validator, temp_dir):
    """Test error handling in validate_path."""
    # Test with a file that can't be read
    no_read_file = temp_dir / "no_read.py"
    violations = validator.validate_path(no_read_file)
    assert len(violations) == 0  # Should handle the error gracefully

def test_validate_directory_error_handling(validator, temp_dir):
    """Test error handling in validate_directory."""
    # Test with a non-existent directory
    non_existent_dir = temp_dir / "non_existent"
    violations = validator.validate_directory(non_existent_dir)
    assert len(violations) == 0  # Should handle the error gracefully

def test_validator_metadata(validator):
    """Test validator metadata methods."""
    assert validator.get_name() == "naming_convention"
    metadata = validator.metadata()
    assert metadata["name"] == "naming_convention"
    assert metadata["group"] == "standards"
    assert "description" in metadata
    assert metadata["version"] == "v1"

def test_validator_dry_run(validator, temp_dir):
    """Test validator dry run functionality."""
    result = validator.run(dry_run=True)
    assert result.status == UnifiedStatus.success
    assert len(result.messages) == 0
    assert result.tool_name == "naming_convention"

def test_validator_execute(validator, temp_dir):
    """Test validator execute method."""
    result = validator.execute()
    assert isinstance(result.status, UnifiedStatus)
    assert result.tool_name == "naming_convention"

@patch('argparse.ArgumentParser.parse_args')
@patch('foundation.di.di_container.DIContainer.resolve')
def test_main_function(mock_resolve, mock_parse_args, temp_dir):
    """Test the main CLI function."""
    # Mock the validator
    mock_validator = MagicMock()
    mock_validator.validate.return_value = MagicMock(
        status=UnifiedStatus.success,
        target=str(temp_dir),
        tool_name="naming_convention",
        version=MagicMock(protocol_version="1.0"),
        messages=[]
    )
    mock_resolve.return_value = mock_validator
    
    # Mock command line arguments
    mock_parse_args.return_value = argparse.Namespace(
        target=str(temp_dir),
        verbose=False
    )
    
    # Test main function
    assert main() == 0
    
    # Test with verbose output
    mock_parse_args.return_value = argparse.Namespace(
        target=str(temp_dir),
        verbose=True
    )
    assert main() == 0
    
    # Test with validation errors
    mock_validator.validate.return_value = MagicMock(
        status=UnifiedStatus.error,
        target=str(temp_dir),
        tool_name="naming_convention",
        version=MagicMock(protocol_version="1.0"),
        messages=[MagicMock(
            summary="Test error",
            file="test.py",
            context={"rule": "Test rule"}
        )]
    )
    assert main() == 1 