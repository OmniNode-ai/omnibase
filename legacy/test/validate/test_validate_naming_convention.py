"""
Test case for naming convention validation.

This module provides test cases for validating naming conventions.
"""

import pytest
from pathlib import Path

from foundation.fixture.fixture_naming_convention import NamingRule, NamingConventionRules


@pytest.fixture
def naming_rules():
    """Fixture providing naming convention rules."""
    return NamingConventionRules()


def test_naming_rule_creation():
    """Test NamingRule creation and pattern compilation."""
    rule = NamingRule(
        name="test_rule",
        pattern=r"^test_\w+\.py$",
        error_message="Test error message",
        description="Test description"
    )
    assert rule.name == "test_rule"
    assert rule.error_message == "Test error message"
    assert rule.description == "Test description"
    assert rule.compiled_pattern is not None


def test_naming_rule_matches():
    """Test NamingRule matches method."""
    rule = NamingRule(
        name="test_rule",
        pattern=r"^test_\w+\.py$",
        error_message="Test error message"
    )
    assert rule.matches("test_valid.py")
    assert not rule.matches("invalid.py")
    assert not rule.matches("test_invalid.txt")


def test_general_file_naming(naming_rules):
    """Test general file naming convention."""
    rule = naming_rules.get_rule("general_file_naming")
    assert rule is not None
    assert rule.matches("valid_file_name.py")
    assert not rule.matches("InvalidFileName.py")
    assert not rule.matches("invalid-file-name.py")
    assert not rule.matches("valid_file_name.txt")


def test_test_file_naming(naming_rules):
    """Test test file naming convention."""
    rule = naming_rules.get_rule("test_file_naming")
    assert rule is not None
    assert rule.matches("test_valid_file.py")
    assert not rule.matches("testInvalidFile.py")
    assert not rule.matches("invalid_test_file.py")
    assert not rule.matches("test_valid_file.txt")


def test_validator_file_naming(naming_rules):
    """Test validator file naming convention."""
    rule = naming_rules.get_rule("validator_file_naming")
    assert rule is not None
    assert rule.matches("validate_valid_file.py")
    assert not rule.matches("validateInvalidFile.py")
    assert not rule.matches("invalid_validate_file.py")
    assert not rule.matches("validate_valid_file.txt")


def test_protocol_file_naming(naming_rules):
    """Test protocol file naming convention."""
    rule = naming_rules.get_rule("protocol_file_naming")
    assert rule is not None
    assert rule.matches("protocol_valid_file.py")
    assert not rule.matches("protocolInvalidFile.py")
    assert not rule.matches("invalid_protocol_file.py")
    assert not rule.matches("protocol_valid_file.txt")


def test_python_file_naming(naming_rules):
    """Test Python file naming convention."""
    rule = naming_rules.get_rule("python_file_naming")
    assert rule is not None
    assert rule.matches("python_valid_file.py")
    assert not rule.matches("pythonInvalidFile.py")
    assert not rule.matches("invalid_python_file.py")
    assert not rule.matches("python_valid_file.txt")


def test_yaml_file_naming(naming_rules):
    """Test YAML file naming convention."""
    rule = naming_rules.get_rule("yaml_file_naming")
    assert rule is not None
    assert rule.matches("yaml_valid_file.yaml")
    assert rule.matches("yaml_valid_file.yml")
    assert not rule.matches("yamlInvalidFile.yaml")
    assert not rule.matches("invalid_yaml_file.yaml")
    assert not rule.matches("yaml_valid_file.txt")


def test_markdown_file_naming(naming_rules):
    """Test Markdown file naming convention."""
    rule = naming_rules.get_rule("markdown_file_naming")
    assert rule is not None
    assert rule.matches("markdown_valid_file.md")
    assert not rule.matches("markdownInvalidFile.md")
    assert not rule.matches("invalid_markdown_file.md")
    assert not rule.matches("markdown_valid_file.txt")


def test_get_rule_for_file(naming_rules):
    """Test getting the appropriate rule for a file path."""
    assert naming_rules.get_rule_for_file("test_valid_file.py").name == "test_file_naming"
    assert naming_rules.get_rule_for_file("validate_valid_file.py").name == "validator_file_naming"
    assert naming_rules.get_rule_for_file("protocol_valid_file.py").name == "protocol_file_naming"
    assert naming_rules.get_rule_for_file("python_valid_file.py").name == "python_file_naming"
    assert naming_rules.get_rule_for_file("valid_file.py").name == "general_file_naming"
    assert naming_rules.get_rule_for_file("yaml_valid_file.yaml").name == "yaml_file_naming"
    assert naming_rules.get_rule_for_file("yaml_valid_file.yml").name == "yaml_file_naming"
    assert naming_rules.get_rule_for_file("markdown_valid_file.md").name == "markdown_file_naming"
    assert naming_rules.get_rule_for_file("unknown.txt") is None


def test_get_rules_by_type(naming_rules):
    """Test getting rules by file type."""
    python_rules = naming_rules.get_rules_by_type("python")
    assert len(python_rules) == 1
    assert python_rules[0].name == "python_file_naming"

    yaml_rules = naming_rules.get_rules_by_type("yaml")
    assert len(yaml_rules) == 1
    assert yaml_rules[0].name == "yaml_file_naming"

    nonexistent_rules = naming_rules.get_rules_by_type("nonexistent")
    assert len(nonexistent_rules) == 0


def test_get_nonexistent_rule(naming_rules):
    """Test getting a rule that doesn't exist."""
    assert naming_rules.get_rule("nonexistent_rule") is None


def test_get_all_rules(naming_rules):
    """Test getting all rules."""
    rules = naming_rules.get_rules()
    assert len(rules) == 7  # We have 7 default rules
    rule_names = {rule.name for rule in rules}
    expected_names = {
        "general_file_naming",
        "test_file_naming",
        "validator_file_naming",
        "protocol_file_naming",
        "python_file_naming",
        "yaml_file_naming",
        "markdown_file_naming"
    }
    assert rule_names == expected_names 