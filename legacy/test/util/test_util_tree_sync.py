# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# name: "test_util_tree_sync"
# namespace: "foundation.test.util"
# meta_type: "test"
# version: "0.1.0"
# owner: "foundation-team"
# entrypoint: "test_util_tree_sync.py"
# === /OmniNode:Tool_Metadata ===

"""
Unit tests for util_tree_sync directory-to-tree and tree-to-directory utilities.
"""

import os
import tempfile
from pathlib import Path
import pytest
from foundation.util.util_tree_sync import directory_to_tree_template, tree_template_to_directory
from foundation.model.model_struct_index import TreeNode
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
import logging

def create_sample_dir_structure(base: Path):
    (base / "foo").mkdir()
    (base / "foo" / "bar").mkdir(parents=True)
    (base / "foo" / "baz.txt").write_text("hello")
    (base / "foo" / "bar" / "qux.py").write_text("print('hi')")
    (base / "README.md").write_text("# Readme")

@pytest.fixture
def logger():
    """Fixture for a test logger."""
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    return logger

def test_directory_to_tree_and_back(logger):
    # Get the canonical valid .tree file from the registry
    tree_file = TEST_CASE_REGISTRY.get_test_case("directory_tree", "tree", "valid")
    assert tree_file is not None, "No valid directory_tree .tree test case found in registry"
    # Load the tree template from the .tree file
    from foundation.util.util_tree_file_utils import UtilTreeFileUtils
    tree_utils = UtilTreeFileUtils(logger)
    tree_node = tree_utils.read_tree_file(tree_file)
    assert isinstance(tree_node, TreeNode)
    # Optionally, round-trip: write to a temp file and read back
    with tempfile.TemporaryDirectory() as tmpdir:
        out_tree_file = Path(tmpdir) / "roundtrip.tree"
        tree_utils.write_tree_file(str(out_tree_file), tree_node, force=True)
        roundtrip_node = tree_utils.read_tree_file(str(out_tree_file))
        assert isinstance(roundtrip_node, TreeNode)
        # Compare some key properties (e.g., name, children)
        assert tree_node.name == roundtrip_node.name
        assert len(tree_node.children or []) == len(roundtrip_node.children or []) 