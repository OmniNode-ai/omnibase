# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_profile_schema"
# namespace: "omninode.tools.test_validate_profile_schema"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:15+00:00"
# last_modified_at: "2025-05-05T13:00:15+00:00"
# entrypoint: "test_validate_profile_schema.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import subprocess
import sys
from pathlib import Path

import pytest
from foundation.protocol.test_helper import ITestHelper
from foundation.script.validation.validator_registry import (
    get_fixture_by_interface,
    get_registered_fixture,
)

# Paths
SCRIPT_PATH = (
    Path(__file__).parents[5]
    / "containers"
    / "foundation"
    / "src"
    / "foundation"
    / "scripts"
    / "validation"
    / "validate_profile_schema.py"
)
VALID_YAML = (
    Path(__file__).parent / "test_cases" / "metadata" / "valid" / "valid_metadata.yaml"
)
INVALID_YAML = (
    Path(__file__).parent / "test_cases" / "metadata" / "invalid" / "missing_owner.yaml"
)


# Use shared temp directory fixture from the registry
@pytest.fixture
def temp_py_dir():
    fixture_cls = get_registered_fixture()["valid_container_yaml_fixture"]
    return fixture_cls().get_fixture()


# --- CLI Tests ---
def test_profile_schema_cli_valid():
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(VALID_YAML), "--verbose"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_profile_schema_cli_invalid():
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(INVALID_YAML), "--verbose"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2


# --- Import Tests ---
def test_profile_schema_import_valid():
    from foundation.script.validation.validate_profile_schema import (
        validate_profile_schema,
    )

    assert validate_profile_schema(VALID_YAML, verbose=False) is True


@pytest.fixture
def profile_schema_validator():
    fixture_cls = get_registered_fixture()["profile_schema_validator_fixture"]
    return fixture_cls().get_fixture()


def test_profile_schema_import_invalid(profile_schema_validator):
    helper = get_fixture_by_interface(ITestHelper)()
    result = profile_schema_validator.validate(INVALID_YAML)
    assert not result.is_valid
    for err in result.errors:
        helper.assert_issue_fields(err)
    helper.assert_has_error(result.errors, "missing", str(INVALID_YAML))