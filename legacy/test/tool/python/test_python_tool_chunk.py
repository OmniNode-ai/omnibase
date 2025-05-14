# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_tool_chunk"
# namespace: "omninode.tools.test_python_tool_chunk"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "test_python_tool_chunk.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===



"""
metadata:
  name: python_tool_chunk_test
  tuple: chunk
  type: tool
  language: python
  registry: true
"""

from typing import Any, Generator

import pytest
from foundation.fixture.validator.python.python_fixture_chunk import ChunkToolFixture
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.util.util_chunk_metrics import UtilChunkMetrics


@pytest.fixture
def chunk_tool() -> Generator[Any, None, None]:
    # Use the registry-compliant fixture
    return ChunkToolFixture().get_fixture(python=True)


def test_chunk_tool_valid_short(chunk_tool: Any) -> None:
    fname: str = TEST_CASE_REGISTRY.get_test_case("chunk", "valid_chunk_short", "valid")
    result = chunk_tool.process(fname)
    assert result.is_valid


def test_chunk_tool_hard_fail(chunk_tool: Any) -> None:
    fname: str = TEST_CASE_REGISTRY.get_test_case(
        "chunk", "invalid_chunk_hard_fail", "invalid"
    )
    result = chunk_tool.process(fname)
    assert not result.is_valid


def test_chunk_tool_error_handling(chunk_tool: Any) -> None:
    class FailingValidator:
        def validate(self, file_path):
            raise RuntimeError("Simulated failure")

    from foundation.script.tool.python.python_tool_chunk import PythonToolChunk

    tool = PythonToolChunk(validator=FailingValidator())
    result = tool.process("dummy.txt")
    assert not result.is_valid
    assert result.errors
    assert any("Simulated failure" in e.message for e in result.errors)