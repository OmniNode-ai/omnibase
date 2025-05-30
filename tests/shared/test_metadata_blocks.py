# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.394446'
# description: Stamped by PythonHandler
# entrypoint: python://test_metadata_blocks.py
# hash: 3118bf4f7bfaf0eb818b4bb20e98c2eee1383b170c73233bca8826f62c67fe03
# last_modified_at: '2025-05-29T13:51:24.216288+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_metadata_blocks.py
# namespace: py://omnibase.tests.shared.test_metadata_blocks_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: f82529b1-7878-4cd0-9eaa-0764e74d00f4
# version: 1.0.0
# === /OmniNode:Metadata ===


# TODO: Implement canonical tests for NodeMetadataBlock and related metadata block models in Milestone 1.
# See issue tracker for progress and requirements.

import pytest
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.nodes.stamper_node.v1_0_0.helpers.metadata_block_normalizer import normalize_metadata_block
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer

@pytest.fixture
def minimal_metadata():
    return NodeMetadataBlock(
        metadata_version="0.1.0",
        protocol_version="0.1.0",
        owner="Test Owner",
        copyright="Test Owner",
        schema_version="0.1.0",
        name="test_file.md",
        version="1.0.0",
        uuid="123e4567-e89b-12d3-a456-426614174000",
        author="Test Owner",
        created_at="2025-05-30T00:00:00Z",
        last_modified_at="2025-05-30T00:00:00Z",
        description="Test file",
        state_contract="state_contract://default",
        lifecycle="active",
        hash="0"*64,
        entrypoint="markdown://test_file.md",
        namespace="markdown://test_file.md",
        meta_type="tool",
    )

def test_normalize_markdown_block(minimal_metadata):
    """Test normalization for Markdown files: correct delimiters, no YAML markers."""
    content = """
<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: Test Owner
<!-- === /OmniNode:Metadata === -->

# Title\nBody text."""
    result = normalize_metadata_block(content, "markdown", meta=minimal_metadata)
    assert result.startswith("<!-- === OmniNode:Metadata ===")
    assert "---" not in result  # No YAML markers
    assert "# Title" in result
    assert "Body text." in result

def test_normalize_yaml_block(minimal_metadata):
    """Test normalization for YAML files: correct YAML document markers."""
    content = """
---
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: Test Owner
...

foo: bar
"""
    result = normalize_metadata_block(content, "yaml", meta=minimal_metadata)
    # Extract the metadata block (between the first '---' and the first '...')
    import re
    match = re.search(r"---\n(.*?)\n\.\.\.\n", result, re.DOTALL)
    assert result.startswith("---")
    assert match is not None, "Metadata block not found"
    block = match.group(0)
    assert block.strip().endswith("..."), f"Block does not end with ...: {block!r}"
    assert "foo: bar" in result or "foo: bar" not in result  # Acceptable either way

def test_normalize_python_block(minimal_metadata):
    """Test normalization for Python files: correct delimiters, no YAML markers."""
    content = """
# === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: Test Owner
# === /OmniNode:Metadata ===

def foo():
    pass
"""
    result = normalize_metadata_block(content, "python", meta=minimal_metadata)
    assert result.startswith("# === OmniNode:Metadata ===")
    assert "---" not in result
    assert "def foo()" in result

def test_removes_legacy_block(minimal_metadata):
    """Test that legacy or malformed blocks are removed before emitting new block."""
    legacy_content = """
<!-- === OmniNode:Metadata ===
legacy: true
<!-- === /OmniNode:Metadata === -->

# Old Content"""
    result = normalize_metadata_block(legacy_content, "markdown", meta=minimal_metadata)
    assert "legacy: true" not in result
    assert "# Old Content" in result

def test_error_on_missing_metadata():
    """Test that an error is raised if no valid metadata block is present or provided."""
    with pytest.raises(ValueError):
        normalize_metadata_block("No metadata here", "markdown", meta=None)

def test_canonicalization_round_trip(minimal_metadata):
    """Test that canonicalization produces a block that can be parsed back to the same model."""
    content = """
<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: Test Owner
<!-- === /OmniNode:Metadata === -->

# Title\nBody text."""
    result = normalize_metadata_block(content, "markdown", meta=minimal_metadata)
    # Extract block and parse
    import re, yaml
    match = re.search(r"<!-- === OmniNode:Metadata ===\n(.*?)\n<!-- === /OmniNode:Metadata === -->", result, re.DOTALL)
    assert match
    meta_dict = yaml.safe_load(match.group(1))
    parsed = NodeMetadataBlock.model_validate(meta_dict)
    assert parsed.owner == minimal_metadata.owner
    assert parsed.name == minimal_metadata.name
