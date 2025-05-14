"""
Naming convention rules fixture.

This module provides fixtures for managing naming convention rules.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern

from foundation.fixture import BaseTestFixture
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.fixture.validator.python import BaseTestFixture


@dataclass
class NamingRule:
    """A rule for validating naming conventions."""
    name: str
    pattern: str
    error_message: str
    description: Optional[str] = None

    def __post_init__(self):
        """Compile the regex pattern after initialization."""
        self._compiled_pattern: Pattern = re.compile(self.pattern)

    @property
    def compiled_pattern(self) -> Pattern:
        """Get the compiled regex pattern."""
        return self._compiled_pattern

    def matches(self, filename: str) -> bool:
        """Check if a filename matches this rule's pattern."""
        return bool(self.compiled_pattern.match(filename))


class NamingConventionRules(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for managing naming convention rules."""

    def get_rules(self) -> List[NamingRule]:
        """Get all registered naming convention rules."""
        return [
            NamingRule(
                name="general_file_naming",
                pattern=r"^[a-z][a-z0-9_]*\.py$",
                error_message="File names must be lowercase and use snake_case",
                description="General file naming convention"
            ),
            NamingRule(
                name="test_file_naming",
                pattern=r"^test_[a-z][a-z0-9_]*\.py$",
                error_message="Test files must start with 'test_' and use snake_case",
                description="Test file naming convention"
            ),
            NamingRule(
                name="validator_file_naming",
                pattern=r"^validate_[a-z][a-z0-9_]*\.py$",
                error_message="Validator files must start with 'validate_' and use snake_case",
                description="Validator file naming convention"
            ),
            NamingRule(
                name="protocol_file_naming",
                pattern=r"^protocol_[a-z][a-z0-9_]*\.py$",
                error_message="Protocol files must start with 'protocol_' and use snake_case",
                description="Protocol file naming convention"
            ),
            NamingRule(
                name="python_file_naming",
                pattern=r"^python_[a-z][a-z0-9_]*\.py$",
                error_message="Python files must start with 'python_' and use snake_case",
                description="Python file naming convention"
            ),
            NamingRule(
                name="yaml_file_naming",
                pattern=r"^yaml_[a-z][a-z0-9_]*\.(yaml|yml)$",
                error_message="YAML files must start with 'yaml_' and use snake_case",
                description="YAML file naming convention"
            ),
            NamingRule(
                name="markdown_file_naming",
                pattern=r"^markdown_[a-z][a-z0-9_]*\.md$",
                error_message="Markdown files must start with 'markdown_' and use snake_case",
                description="Markdown file naming convention"
            )
        ]

    def get_rule(self, name: str) -> Optional[NamingRule]:
        """Get a specific naming convention rule by name."""
        for rule in self.get_rules():
            if rule.name == name:
                return rule
        return None

    def get_rules_by_type(self, file_type: str) -> List[NamingRule]:
        """Get all rules applicable to a specific file type."""
        return [rule for rule in self.get_rules() if rule.name.startswith(f"{file_type}_")]

    def get_rule_for_file(self, file_path: str) -> Optional[NamingRule]:
        """Get the appropriate rule for a given file path."""
        if file_path.endswith(".py"):
            if file_path.startswith("test_"):
                return self.get_rule("test_file_naming")
            elif file_path.startswith("validate_"):
                return self.get_rule("validator_file_naming")
            elif file_path.startswith("protocol_"):
                return self.get_rule("protocol_file_naming")
            elif file_path.startswith("python_"):
                return self.get_rule("python_file_naming")
            else:
                return self.get_rule("general_file_naming")
        elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
            return self.get_rule("yaml_file_naming")
        elif file_path.endswith(".md"):
            return self.get_rule("markdown_file_naming")
        return None 