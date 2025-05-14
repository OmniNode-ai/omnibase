# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_tool_chunk"
# namespace: "omninode.tools.test_tool_chunk"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "test_tool_chunk.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===



"""
metadata:
  name: tool_chunk_test
  tuple: chunk
  type: tool
  language: shell
  registry: true
"""

import pytest
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.fixture.fixture_registry import FIXTURE_REGISTRY


@pytest.fixture
def chunk_tool():
    # Use the fixture registry to obtain the chunk tool fixture
    fixture = FIXTURE_REGISTRY.get_fixture("chunk_tool_fixture")
    return fixture.get_fixture()


def test_chunk_tool_valid_short(chunk_tool):
    # Use the registry to get the canonical test case file path
    fname = TEST_CASE_REGISTRY.get_test_case("chunk", "valid_chunk_tool_basic", "valid")
    result = chunk_tool.process(fname)
    assert result.is_valid


def test_chunk_tool_hard_fail(chunk_tool):
    # Use the registry to get the canonical invalid test case file path
    fname = TEST_CASE_REGISTRY.get_test_case("chunk", "invalid_chunk_tool_edge", "invalid")
    result = chunk_tool.process(fname)
    assert not result.is_valid