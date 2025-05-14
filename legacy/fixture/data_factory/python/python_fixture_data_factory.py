# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_data_factory"
# namespace: "omninode.tools.test_python_fixture_data_factory"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:25+00:00"
# last_modified_at: "2025-05-05T13:00:25+00:00"
# entrypoint: "test_python_fixture_data_factory.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture']
# base_class: ['BaseTestFixture']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Shared test data factory fixture for validator tests.
Fixtures are registry-registered, DI-compliant, and use schemas/templates for data generation.
"""

import random
from typing import Any, Dict

from foundation.script.validate.validate_registry import register_fixture
from foundation.fixture import BaseTestFixture
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture


class ValidMetadataFactoryFixture(BaseTestFixture, ProtocolValidateFixture):
    """Factory fixture for generating valid metadata dicts."""

    def get_fixture(self) -> Dict[str, Any]:
        return {
            "name": f"test-{random.randint(1000,9999)}",
            "version": "1.0.0",
            "owner": "test@example.com",
        }


class InvalidMetadataFactoryFixture(BaseTestFixture, ProtocolValidateFixture):
    """Factory fixture for generating invalid metadata dicts."""

    def get_fixture(self) -> Dict[str, Any]:
        return {
            "name": "",
            "version": "not-a-version",
            # missing owner
        }


# Register fixture in the registry
register_fixture(
    name="valid_metadata_factory_fixture",
    fixture=ValidMetadataFactoryFixture,
    description="Factory fixture for generating valid metadata dicts",
)
register_fixture(
    name="invalid_metadata_factory_fixture",
    fixture=InvalidMetadataFactoryFixture,
    description="Factory fixture for generating invalid metadata dicts",
)