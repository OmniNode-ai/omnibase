# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_chunk"
# namespace: "omninode.tools.test_python_fixture_chunk"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "test_python_fixture_chunk.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture']
# base_class: ['BaseTestFixture']
# mock_safe: true
# === /OmniNode:Metadata ===



"""
DI/registry-compliant fixture for chunk validator and tool.
"""

from typing import Any

import structlog
from foundation.script.validate.python.python_validate_chunk import PythonValidateChunk
from foundation.fixture import BaseTestFixture
from foundation.script.tool.python.python_tool_chunk import PythonToolChunk
import pytest
from foundation.util.util_chunk_metrics import UtilChunkMetrics
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture

# Register the chunk validator and tool fixtures for DI/registry compliance
from foundation.script.validate.validate_registry import register_fixture

from foundation.fixture.validator.python.python_fixture_chunk import (
    PythonTestFixtureChunk,
)
from foundation.fixture.validator.python.python_fixture_chunk import ChunkToolFixture

class PythonTestFixtureChunk(BaseTestFixture, ProtocolValidateFixture):
    def get_fixture(self, python: bool = False) -> Any:
        # Import the correct validator based on the python flag
        if python:
            from foundation.script.validate.python.python_validate_chunk import (
                PythonValidateChunk,
            )
            return PythonValidateChunk(chunk_metrics=UtilChunkMetrics)
        else:
            from foundation.script.validate.python.python_validate_chunk_cli import PythonValidateChunkCLI
            return PythonValidateChunkCLI()


class ChunkToolFixture(BaseTestFixture, ProtocolValidateFixture):
    def get_fixture(self, python: bool = False) -> Any:
        # Import the correct tool based on the python flag
        logger = structlog.get_logger("chunk_tool_test")
        validator = PythonValidateChunk(logger=logger, chunk_metrics=UtilChunkMetrics)
        return PythonToolChunk(validator=validator, logger=logger, chunk_metrics=UtilChunkMetrics)

register_fixture(
    name="python_test_fixture_chunk",
    fixture=PythonTestFixtureChunk,
    description="DI/registry-compliant fixture for chunk validator (Python)",
)

register_fixture(
    name="chunk_tool_fixture",
    fixture=ChunkToolFixture,
    description="DI/registry-compliant fixture for chunk tool (Python)",
)

register_fixture(
    name="chunk_validator_fixture",
    fixture=lambda: PythonValidateChunk(config={}, logger=structlog.get_logger("test_chunk_validator"), chunk_metrics=UtilChunkMetrics),
    description="DI/registry-compliant fixture for chunk validator (Python, direct instance)",
)

def test_chunk_validator_fixture_non_python() -> None:
    from foundation.test.fixture.python.test_python_fixture_chunk import (
        PythonTestFixtureChunk,
    )

    fixture = PythonTestFixtureChunk()
    validator = fixture.get_fixture(python=False)
    assert validator is not None


def test_chunk_tool_fixture_non_python() -> None:
    from foundation.test.fixture.python.test_python_fixture_chunk import ChunkToolFixture

    fixture = ChunkToolFixture()
    tool = fixture.get_fixture(python=False)
    assert tool is not None


def test_chunk_validator_fixture_python() -> None:
    from foundation.script.validate.python.python_validate_chunk import (
        PythonValidateChunk,
    )
    from foundation.test.fixture.python.test_python_fixture_chunk import (
        PythonTestFixtureChunk,
    )

    fixture = PythonTestFixtureChunk()
    validator = fixture.get_fixture(python=True)
    assert isinstance(validator, PythonValidateChunk)


def test_chunk_tool_fixture_python() -> None:
    from foundation.test.fixture.python.test_python_fixture_chunk import ChunkToolFixture

    fixture = ChunkToolFixture()
    tool = fixture.get_fixture(python=True)
    assert isinstance(tool, PythonToolChunk)

@pytest.fixture(scope="module")
def chunk_validator_fixture():
    logger = structlog.get_logger("test_chunk_validator")
    return PythonValidateChunk(config={}, logger=logger, chunk_metrics=UtilChunkMetrics)