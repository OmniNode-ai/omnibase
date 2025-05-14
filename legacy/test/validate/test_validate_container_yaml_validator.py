#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_container_yaml_validator"
# namespace: "omninode.tools.test_validate_container_yaml_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:13+00:00"
# last_modified_at: "2025-05-05T13:00:13+00:00"
# entrypoint: "test_validate_container_yaml_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""Module that handles functionality for the OmniNode platform.

This module provides:
- Core interfaces for standard operations
- Validation logic and exception handling
- Integration with other system components

Intended to be customized and extended by consumers based on
specific use cases and requirements.
"""

from pathlib import Path

import pytest
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.fixture.fixture_helper import TestHelper
from foundation.script.validate.python.python_validate_container_yaml import ContainerYAMLValidator
from foundation.script.validate.validate_registry import (
    get_fixture_by_interface,
    get_registered_fixture,
)
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.test.util.test_in_memory_validation_mixin import InMemoryValidationTestMixin


# Use shared file fixture from the registry
@pytest.fixture
def valid_container_yaml_dir():
    fixture_cls = get_registered_fixture("valid_container_yaml_fixture")
    return fixture_cls().get_fixture()


@pytest.fixture
def invalid_container_yaml_dir():
    fixture_cls = get_registered_fixture("invalid_container_yaml_fixture")
    return fixture_cls().get_fixture()


def test_valid_container_yaml():
    fname = TEST_CASE_REGISTRY.get_test_case("container_yaml", "valid_container_yaml", "valid")
    validator = ContainerYAMLValidator()
    result = validator.validate(Path(fname))
    assert (
        result.is_valid
    ), f"Expected valid container.yaml to pass, got errors: {result.errors}"


def test_invalid_container_yaml():
    helper = get_registered_fixture("test_helper")()
    fname = TEST_CASE_REGISTRY.get_test_case("container_yaml", "invalid_container_yaml", "invalid")
    validator = ContainerYAMLValidator()
    result = validator.validate(Path(fname))
    assert not result.is_valid, "Expected invalid container.yaml to fail validation"
    for err in result.errors:
        helper.assert_issue_fields(err)
    # Check for at least one error message (schema/content error)
    assert len(result.errors) > 0, "Expected at least one error for invalid container.yaml"


def test_valid_container_yaml_with_warnings(tmp_path):
    helper = get_registered_fixture("test_helper")()
    yaml_content = """
name: valid-container
version: 1.0.0
description: A valid test container
agent_class: processor
priority: medium
memory_profile: medium
"""
    yaml_file = tmp_path / "container.yaml"
    yaml_file.write_text(yaml_content)
    validator = ContainerYAMLValidator()
    result = validator.validate(yaml_file)
    assert result.is_valid
    for warn in result.warnings:
        helper.assert_issue_fields(warn)
    helper.assert_has_warning(result.warnings, "retry_policy", str(yaml_file))
    helper.assert_has_warning(result.warnings, "tags", str(yaml_file))


def test_valid_container_yaml_complete(tmp_path):
    helper = get_registered_fixture("test_helper")()
    yaml_content = """
name: valid-container
version: 1.0.0
description: A valid test container
agent_class: processor
priority: medium
memory_profile: medium
retry_policy:
  max_retries: 3
tags:
  - test
  - production
"""
    yaml_file = tmp_path / "container.yaml"
    yaml_file.write_text(yaml_content)
    validator = ContainerYAMLValidator()
    result = validator.validate(yaml_file)
    assert result.is_valid
    assert not result.warnings
    for err in result.errors:
        helper.assert_issue_fields(err)


class TestContainerYAMLValidator(InMemoryValidationTestMixin):
    def test_valid_container_yaml_with_warnings(self):
        helper = get_registered_fixture("test_helper")()
        yaml_content = """
name: valid-container
version: 1.0.0
description: A valid test container
agent_class: processor
priority: medium
memory_profile: medium
"""
        validator = ContainerYAMLValidator()
        expected = {"is_valid": True, "errors": 0, "warnings": 2}
        self.run_in_memory_validation(validator, yaml_content, expected)

    def test_valid_container_yaml_complete(self):
        helper = get_registered_fixture("test_helper")()
        yaml_content = """
name: valid-container
version: 1.0.0
description: A valid test container
agent_class: processor
priority: medium
memory_profile: medium
retry_policy:
  max_retries: 3
tags:
  - test
  - production
"""
        validator = ContainerYAMLValidator()
        expected = {"is_valid": True, "errors": 0, "warnings": 0}
        self.run_in_memory_validation(validator, yaml_content, expected)