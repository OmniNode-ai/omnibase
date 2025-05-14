# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_env_secrets_validator"
# namespace: "omninode.tools.test_validate_env_secrets_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:16+00:00"
# last_modified_at: "2025-05-05T13:00:16+00:00"
# entrypoint: "test_validate_env_secrets_validator.py"
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
def env_secrets_validator():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    return fixture_cls().get_fixture()


@pytest.fixture
def valid_env_dir():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    return fixture_cls().get_fixture()


@pytest.fixture
def invalid_env_dir():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    return fixture_cls().get_fixture()


@pytest.fixture
def missing_env_dir():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    return fixture_cls().get_fixture()


def test_valid_env(valid_env_dir, env_secrets_validator):
    result = env_secrets_validator.validate(valid_env_dir)
    assert result.is_valid
    assert not result.errors


def test_invalid_env(invalid_env_dir, env_secrets_validator):
    result = env_secrets_validator.validate(invalid_env_dir)
    assert not result.is_valid
    assert any("Potential" in e.message for e in result.errors)


def test_missing_env(missing_env_dir, env_secrets_validator):
    result = env_secrets_validator.validate(missing_env_dir)
    # Should pass because no files to check means no secrets found
    assert result.is_valid
    assert not result.errors