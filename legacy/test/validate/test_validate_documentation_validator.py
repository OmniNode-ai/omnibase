# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_documentation_validator"
# namespace: "omninode.tools.test_validate_documentation_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:15+00:00"
# last_modified_at: "2025-05-05T13:00:15+00:00"
# entrypoint: "test_validate_documentation_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import pytest
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.fixture.fixture_helper import TestHelper
from foundation.script.validate.validate_registry import get_fixture_by_interface


@pytest.fixture
def documentation_validator():
    return DocumentationValidator()


@pytest.fixture
def valid_readme_dir():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    return fixture_cls().get_fixture()


@pytest.fixture
def invalid_readme_dir():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    return fixture_cls().get_fixture()


@pytest.fixture
def missing_readme_dir():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    return fixture_cls().get_fixture()


def test_valid_documentation(valid_readme_dir, documentation_validator):
    helper = get_fixture_by_interface(TestHelper)()
    result = documentation_validator.validate(valid_readme_dir)
    assert result.is_valid
    assert not result.errors


def test_invalid_documentation(invalid_readme_dir, documentation_validator):
    helper = get_fixture_by_interface(TestHelper)()
    result = documentation_validator.validate(invalid_readme_dir)
    assert not result.is_valid
    for err in result.errors:
        helper.assert_issue_fields(err)
    helper.assert_has_error(result.errors, "Required section", "README.md")
    helper.assert_has_error(result.errors, "too short", "README.md")


def test_missing_readme(missing_readme_dir, documentation_validator):
    helper = get_fixture_by_interface(TestHelper)()
    result = documentation_validator.validate(missing_readme_dir)
    assert not result.is_valid
    for err in result.errors:
        helper.assert_issue_fields(err)
    helper.assert_has_error(
        result.errors, "README.md not found", str(missing_readme_dir / "README.md")
    )