# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_mock"
# namespace: "omninode.tools.test_python_fixture_mock"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:26+00:00"
# last_modified_at: "2025-05-05T13:00:26+00:00"
# entrypoint: "test_python_fixture_mock.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture']
# base_class: ['BaseTestFixture']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Shared mock/stub fixture for external dependencies in validator tests.
Fixtures are registry-registered, DI-compliant, and use abstract base classes.
"""

from unittest.mock import MagicMock

from foundation.script.validate.validate_registry import register_fixture
from foundation.fixture import BaseTestFixture
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture


class MockApiClientFixture(BaseTestFixture, ProtocolValidateFixture):
    """Mock fixture for an external API client."""

    def get_fixture(self):
        mock_client = MagicMock()
        mock_client.get.return_value = {"status": "ok", "data": {}}
        mock_client.post.return_value = {"status": "created"}
        return mock_client


# Register the mock fixture in the registry
register_fixture(
    name="mock_api_client_fixture",
    fixture=MockApiClientFixture,
    description="Mock fixture for an external API client",
)