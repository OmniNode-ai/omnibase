# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_metadata_block_noncompliant"
# namespace: "omninode.tools.test_python_fixture_metadata_block_noncompliant"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:25+00:00"
# last_modified_at: "2025-05-05T13:00:25+00:00"
# entrypoint: "test_python_fixture_metadata_block_noncompliant.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture']
# base_class: ['BaseTestFixture']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
DI/registry-compliant fixture for metadata_block validator.
"""

from typing import Any

from foundation.script.validate.validate_registry import register_fixture
from foundation.fixture import BaseTestFixture
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.script.validate.python.python_validate_metadata_block import PythonValidateMetadataBlock
from foundation.fixture.metadata.python.python_fixture_metadata_block import (
    PythonTestFixtureMetadataBlock,
)


class PythonTestFixtureMetadataBlock(BaseTestFixture, ProtocolValidateFixture):
    def get_fixture(self, python: bool = False) -> Any:
        return PythonValidateMetadataBlock()


register_fixture(
    name="python_test_fixture_metadata_block",
    fixture=PythonTestFixtureMetadataBlock,
    description="DI/registry-compliant fixture for metadata_block validator (Python)",
)


def test_metadata_block_fixture() -> None:
    from foundation.script.validate.python.python_validate_metadata_block import PythonValidateMetadataBlock
    from foundation.test.fixture.python.python_test_fixture_metadata_block import (
        PythonTestFixtureMetadataBlock,
    )

    fixture = PythonTestFixtureMetadataBlock()
    validator = fixture.get_fixture()
    assert isinstance(validator, PythonValidateMetadataBlock)