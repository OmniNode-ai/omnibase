# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_api"
# namespace: "omninode.tools.test_validate_api"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:15+00:00"
# last_modified_at: "2025-05-05T13:00:15+00:00"
# entrypoint: "test_validate_api.py"
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
def api_validator():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    return fixture_cls().get_fixture()


def test_validate_api_with_missing_spec(tmp_path, api_validator):
    result = api_validator.validate(tmp_path)
    assert not result.is_valid
    assert any(
        "No OpenAPI/Swagger specification found" in err.message for err in result.errors
    )


def test_validate_api_with_invalid_yaml(tmp_path, api_validator):
    spec_path = tmp_path / "openapi.yaml"
    spec_path.write_text(":invalid: yaml: : :")
    result = api_validator.validate(tmp_path)
    assert not result.is_valid
    assert any(
        "Failed to parse API specification" in err.message for err in result.errors
    )