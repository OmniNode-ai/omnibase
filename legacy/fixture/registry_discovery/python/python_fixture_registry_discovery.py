# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_registry_discovery"
# namespace: "omninode.tools.test_python_fixture_registry_discovery"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:25+00:00"
# last_modified_at: "2025-05-05T13:00:25+00:00"
# entrypoint: "test_python_fixture_registry_discovery.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture']
# base_class: ['BaseTestFixture']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Registry discovery fixture for validator and fixture registration tests.
Fixture is registry-registered, DI-compliant, and provides discovery utilities.
"""

from typing import Any, List

from foundation.script.validate.validate_registry import (
    get_registered_fixture,
    register_fixture,
)
from foundation.fixture import BaseTestFixture
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture


class RegistryDiscoveryFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for asserting registry discovery of validators and fixture."""

    def get_fixture(self) -> Any:
        class RegistryDiscovery:
            @staticmethod
            def list_fixture() -> List[str]:
                return list(get_registered_fixture().keys())

            # Removed list_validators due to missing implementation

        return RegistryDiscovery


# Register the registry discovery fixture
register_fixture(
    name="registry_discovery_fixture",
    fixture=RegistryDiscoveryFixture,
    description="Fixture for asserting registry discovery of validators and fixture",
)