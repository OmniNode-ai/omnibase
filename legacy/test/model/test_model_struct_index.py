#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_model_struct_index"
# namespace: "omninode.tools.test_model_struct_index"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-06T00:00:00+00:00"
# last_modified_at: "2025-05-06T00:00:00+00:00"
# entrypoint: "test_model_struct_index.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseModel']
# base_class: ['BaseModel']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Test cases for model_struct_index.py
"""
import pytest
from foundation.model.model_struct_index import TreeNode
from datetime import datetime

def test_tree_node_basic():
    """Test basic TreeNode creation and validation."""
    node = TreeNode(
        name="test_file.py",
        type="file",
        size=1024,
        mtime=datetime.now().timestamp(),
        metadata={"key": "value"}
    )
    assert node.name == "test_file.py"
    assert node.type == "file"
    assert node.size == 1024
    assert node.metadata == {"key": "value"}
    assert node.children is None

def test_tree_node_directory():
    """Test TreeNode with children (directory)."""
    child1 = TreeNode(name="child1.py", type="file")
    child2 = TreeNode(name="child2.py", type="file")
    parent = TreeNode(
        name="test_dir",
        type="directory",
        children=[child1, child2]
    )
    assert parent.name == "test_dir"
    assert parent.type == "directory"
    assert len(parent.children) == 2
    assert parent.children[0].name == "child1.py"
    assert parent.children[1].name == "child2.py"

def test_tree_node_optional_fields():
    """Test TreeNode with optional fields omitted."""
    node = TreeNode(name="test.py", type="file")
    assert node.name == "test.py"
    assert node.type == "file"
    assert node.size is None
    assert node.mtime is None
    assert node.metadata is None
    assert node.children is None

def test_tree_node_invalid_type():
    """Test TreeNode with invalid type."""
    with pytest.raises(ValueError):
        TreeNode(name="test.py", type="invalid")

def test_tree_node_nested():
    """Test nested TreeNode structure."""
    grandchild = TreeNode(name="grandchild.py", type="file")
    child = TreeNode(
        name="child_dir",
        type="directory",
        children=[grandchild]
    )
    parent = TreeNode(
        name="parent_dir",
        type="directory",
        children=[child]
    )
    assert parent.name == "parent_dir"
    assert parent.type == "directory"
    assert len(parent.children) == 1
    assert parent.children[0].name == "child_dir"
    assert len(parent.children[0].children) == 1
    assert parent.children[0].children[0].name == "grandchild.py"

def test_tree_node_metadata():
    """Test TreeNode with complex metadata."""
    metadata = {
        "owner": "test_user",
        "permissions": "rwxr-xr-x",
        "created_at": "2025-05-06T00:00:00Z",
        "tags": ["test", "example"]
    }
    node = TreeNode(
        name="test.py",
        type="file",
        metadata=metadata
    )
    assert node.metadata == metadata
    assert node.metadata["owner"] == "test_user"
    assert node.metadata["tags"] == ["test", "example"] 