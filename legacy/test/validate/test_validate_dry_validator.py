# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_dry_validator"
# namespace: "omninode.tools.test_validate_dry_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:17+00:00"
# last_modified_at: "2025-05-05T13:00:17+00:00"
# entrypoint: "test_validate_dry_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import pytest
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.fixture.fixture_helper import TestHelper
from foundation.script.validate.validate_dry import DRYValidator
from foundation.script.validate.validate_registry import (
    get_fixture_by_interface,
    get_registered_fixture,
)


@pytest.fixture
def valid_codebase():
    fixture_cls = get_registered_fixture()["valid_container_yaml_fixture"]
    return fixture_cls().get_fixture()


@pytest.fixture
def duplicate_codebase(tmp_path):
    # Create two .py files with identical function bodies (min_lines=5, min_occurrences=2)
    code = """
def repeat():
    x = 1
    y = 2
    z = x + y
    print(z)
    return z
"""
    (tmp_path / "c.py").write_text(code)
    (tmp_path / "d.py").write_text(code)
    return tmp_path


@pytest.fixture
def empty_codebase(tmp_path):
    # No .py files
    return tmp_path


def test_valid_codebase(valid_codebase):
    validator = DRYValidator()
    result = validator.validate(valid_codebase)
    assert result.is_valid
    assert not result.errors


def test_duplicate_codebase(duplicate_codebase):
    helper = get_fixture_by_interface(ITestHelper)()
    validator = DRYValidator()
    result = validator.validate(duplicate_codebase)
    assert not result.is_valid
    for err in result.errors:
        helper.assert_issue_fields(err)
    helper.assert_has_error(
        result.errors, "Duplicate code block found", str(duplicate_codebase / "c.py")
    )


def test_empty_codebase(empty_codebase):
    validator = DRYValidator()
    result = validator.validate(empty_codebase)
    assert result.is_valid
    assert not result.errors


def test_duplicate_code_block(tmp_path):
    helper = get_fixture_by_interface(ITestHelper)()
    # .. rest of the test ..