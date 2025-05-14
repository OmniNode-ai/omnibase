# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_validator"
# namespace: "omninode.tools.test_python_fixture_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "test_python_fixture_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture', 'ProtocolValidateFixture']
# base_class: ['BaseTestFixture', 'ProtocolValidateFixture']
# mock_safe: true
# === /OmniNode:Metadata ===



"""
Shared validator instance fixture for foundation tests.
All fixture are registry-registered, DI-compliant, and inherit from BaseTestFixture.
"""

from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.script.validate.validate_registry import register_fixture

from foundation.fixture import BaseTestFixture
from foundation.script.validate.python.python_validate_chunk import PythonValidateChunk


# Only keep the chunk validator fixture for canary test
class ChunkProtocolValidateFixture(BaseTestFixture, ProtocolValidateFixture):
    def get_fixture(self, python=False):
        if python:
            from foundation.script.validate.python.python_validate_chunk import (
                PythonValidateChunk,
            )
            return PythonValidateChunk()
        else:
            from foundation.script.validate.validate_chunk import ChunkValidator

            return ChunkValidator()


register_fixture(
    name="chunk_validator_fixture",
    fixture=ChunkProtocolValidateFixture,
    description="DI/registry-compliant fixture for ChunkValidator",
    interface=ProtocolValidateFixture,
)