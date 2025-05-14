"""
Test registry for naming convention rules.

This module provides a registry for managing naming convention rules in tests.
"""

from typing import Dict, List, Optional

from foundation.fixture import BaseTestFixture
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.fixture.fixture_naming_convention_rules import NamingRule, TestNamingConventionRules


class TestNamingConventionRegistry(BaseTestFixture, ProtocolValidateFixture):
    """Test registry for managing naming convention rules."""

    def __init__(self):
        """Initialize the registry with default rules."""
        self._rules: Dict[str, NamingRule] = {}
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register the default naming convention rules."""
        rules_fixture = TestNamingConventionRules()
        for rule in rules_fixture.get_rules():
            self.register_rule(rule)

    def register_rule(self, rule: NamingRule) -> None:
        """Register a new naming convention rule."""
        self._rules[rule.name] = rule

    def get_rule(self, name: str) -> Optional[NamingRule]:
        """Get a specific naming convention rule by name."""
        return self._rules.get(name)

    def get_rules(self) -> List[NamingRule]:
        """Get all registered naming convention rules."""
        return list(self._rules.values())

    def get_rules_by_type(self, file_type: str) -> List[NamingRule]:
        """Get all rules applicable to a specific file type."""
        return [rule for rule in self._rules.values() if rule.name.startswith(f"{file_type}_")]

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