#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_container_validator"
# namespace: "omninode.tools.test_validate_container_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:15+00:00"
# last_modified_at: "2025-05-05T13:00:15+00:00"
# entrypoint: "test_validate_container_validator.py"
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


import pytest
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.fixture.fixture_helper import TestHelper
from foundation.script.validate.validate_registry import get_fixture_by_interface
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.test.util.test_in_memory_validation_mixin import InMemoryValidationTestMixin


@pytest.fixture
def validator():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    return fixture_cls().get_fixture()


class TestContainerValidator(InMemoryValidationTestMixin):
    def test_required_files_present(self, validator):
        fname = TEST_CASE_REGISTRY.get_test_case("container_validator", "valid_required_files_present", "valid")
        with open(fname) as f:
            content = f.read()
        config = {
            "rules": {
                "required_files": ["Dockerfile", "README.md"],
                "naming_pattern": r"^[a-z0-9\-]+$",
            }
        }
        result = validator.validate_content(content, config, directory_name="valid-container")
        assert result.is_valid
        assert not result.errors

    def test_missing_required_file(self, validator):
        helper = get_fixture_by_interface(TestHelper)()
        fname = TEST_CASE_REGISTRY.get_test_case("container_validator", "invalid_missing_required_file", "invalid")
        with open(fname) as f:
            content = f.read()
        config = {
            "rules": {
                "required_files": ["Dockerfile", "README.md"],
                "naming_pattern": r"^[a-z0-9\-]+$",
            }
        }
        result = validator.validate_content(content, config, directory_name="valid-container")
        assert not result.is_valid
        for err in result.errors:
            helper.assert_issue_fields(err)
        assert any("required file" in e.message.lower() for e in result.errors)

    def test_container_name_pattern(self, tmp_path, validator):
        good = tmp_path / "valid-container"
        good.mkdir()
        (good / "Dockerfile").write_text("FROM python:3.11\n")
        (good / "README.md").write_text("Container docs\n")
        result = validator.validate(good)
        assert result.is_valid
        assert not result.errors

    def test_container_name_pattern_fail(self, validator):
        helper = get_fixture_by_interface(TestHelper)()
        fname = TEST_CASE_REGISTRY.get_test_case("container_validator", "invalid_container_name_pattern", "invalid")
        with open(fname) as f:
            content = f.read()
        config = {
            "rules": {
                "required_files": ["Dockerfile", "README.md"],
                "naming_pattern": r"^[a-z0-9\-]+$",
            }
        }
        result = validator.validate_content(content, config, directory_name="InvalidContainer!")
        assert not result.is_valid
        for err in result.errors:
            helper.assert_issue_fields(err)
        assert any("does not match pattern" in e.message.lower() for e in result.errors)

    def test_dockerfile_size_within_limit(self, tmp_path, validator):
        (tmp_path / "Dockerfile").write_text("FROM python:3.11\n" * 5)
        (tmp_path / "README.md").write_text("Container docs\n")
        result = validator.validate(tmp_path)
        assert result.is_valid
        assert not result.errors

    def test_dockerfile_size_exceeds_limit(self, tmp_path, validator):
        helper = get_fixture_by_interface(TestHelper)()
        (tmp_path / "Dockerfile").write_text("FROM python:3.11\n" * 20)
        (tmp_path / "README.md").write_text("Container docs\n")
        result = validator.validate(tmp_path)
        assert not result.is_valid
        for err in result.errors:
            helper.assert_issue_fields(err)
        helper.assert_has_error(
            result.errors,
            "Dockerfile exceeds maximum size",
            str(tmp_path / "Dockerfile"),
        )

    def test_init_py_required_present(self, tmp_path, validator):
        (tmp_path / "Dockerfile").write_text("FROM python:3.11\n")
        (tmp_path / "README.md").write_text("Container docs\n")
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "mod.py").write_text("print('hi')\n")
        result = validator.validate(tmp_path)
        assert result.is_valid
        assert not result.errors

    def test_init_py_required_missing(self, tmp_path, validator):
        helper = get_fixture_by_interface(TestHelper)()
        (tmp_path / "Dockerfile").write_text("FROM python:3.11\n")
        (tmp_path / "README.md").write_text("Container docs\n")
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "mod.py").write_text("print('hi')\n")
        result = validator.validate(tmp_path)
        assert not result.is_valid
        for err in result.errors:
            helper.assert_issue_fields(err)
        helper.assert_has_error(result.errors, "Missing __init__.py", str(pkg))

    def test_init_py_ignored(self, tmp_path, validator):
        (tmp_path / "Dockerfile").write_text("FROM python:3.11\n")
        (tmp_path / "README.md").write_text("Container docs\n")
        mig = tmp_path / "migrations"
        mig.mkdir()
        (mig / "mod.py").write_text("print('hi')\n")
        result = validator.validate(tmp_path)
        assert result.is_valid
        assert not result.errors

    def test_non_directory_target(self, tmp_path, validator):
        helper = get_fixture_by_interface(TestHelper)()
        file_target = tmp_path / "not_a_dir.txt"
        file_target.write_text("not a dir")
        result = validator.validate(file_target)
        assert not result.is_valid
        for err in result.errors:
            helper.assert_issue_fields(err)
        helper.assert_has_error(result.errors, "is not a directory", str(file_target))

    def test_happy_path(self, tmp_path, validator):
        (tmp_path / "Dockerfile").write_text("FROM python:3.11\n")
        (tmp_path / "README.md").write_text("Container docs\n")
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "mod.py").write_text("print('hi')\n")
        result = validator.validate(tmp_path)
        assert result.is_valid
        assert not result.errors