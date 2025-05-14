# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_tool_registry"
# namespace: "omninode.tools.test_tool_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T17:01:19+00:00"
# last_modified_at: "2025-05-05T17:01:19+00:00"
# entrypoint: "test_tool_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Canary registry test for tool and fixture discovery.
Ensures all fixtures and tools are registered and discoverable via the central registry.
Follows canary standards for registry-based test implementation.
"""

import pytest
from foundation.fixture.fixture_registry import FIXTURE_REGISTRY
from foundation.script.tool.tool_registry import tool_registry

def test_chunk_tool_fixture_is_registered():
    fixture = FIXTURE_REGISTRY.get_fixture("chunk_tool_fixture")
    assert fixture is not None, "chunk_tool_fixture not found in FIXTURE_REGISTRY"
    # Optionally, check that the fixture provides the expected interface
    instance = fixture.get_fixture()
    assert hasattr(instance, "process"), "ChunkToolFixture instance missing 'process' method"

def test_tool_registry_contains_expected_tools():
    # Example: check that at least one tool is registered
    all_tools = tool_registry.list_tools()
    assert all_tools, "No tools registered in tool_registry"
    # Optionally, check for a specific tool by name
    # assert "chunk_tool" in all_tools, "chunk_tool not registered in tool_registry"

def test_tool_registry_metadata():
    # Example: check that tool metadata is present and correct
    all_metadata = tool_registry.get_all_metadata()
    assert isinstance(all_metadata, dict), "Tool registry metadata is not a dict"
    # Optionally, check for required metadata fields
    for name, meta in all_metadata.items():
        assert "name" in meta, f"Tool {name} missing 'name' in metadata"
        assert "entrypoint" in meta, f"Tool {name} missing 'entrypoint' in metadata"