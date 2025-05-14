from typing import Any, Dict, Optional
import pytest
from foundation.protocol.protocol_test_tree_file_utils import ProtocolTestTreeFileUtils
from foundation.util.util_tree_file_utils import UtilTreeFileUtils
import os
import yaml

class FixtureTreeFileUtils:
    """
    Mock/in-memory implementation of the tree file utility protocol for use in tests.
    Simulates reading and writing .tree files and directory trees without touching the file system.
    """
    def __init__(self):
        self.trees: Dict[str, Any] = {}

    def add_tree(self, name: str, tree: Any) -> None:
        self.trees[name] = tree

    def get_tree(self, name: str) -> Optional[Any]:
        return self.trees.get(name)

    def read_tree_file(self, path: str) -> Any:
        # Simulate reading a .tree file by returning a stored tree
        return self.trees.get(path)

    def write_tree_file(self, path: str, tree: Any) -> None:
        # Simulate writing a .tree file by storing it in memory
        self.trees[path] = tree

    def directory_to_tree_template(self, root_dir: str) -> Any:
        """
        Recursively walk a directory and return a tree_sync.TreeNode Pydantic model.
        Args:
            root_dir: Root directory path to scan.
        Returns:
            tree_sync.TreeNode representing the structure.
        """
        from foundation.util.util_tree_sync import directory_to_tree_template
        return directory_to_tree_template(root_dir)

    def compute_tree_hash(self, tree: Any) -> str:
        """
        Compute a canonical hash of the .tree structure for test purposes.
        Uses the real UtilTreeFileUtils if available, else returns a dummy hash.
        """
        try:
            from foundation.util.util_tree_file_utils import UtilTreeFileUtils
            # Use a dummy logger for the real implementation
            real_utils = UtilTreeFileUtils(logger=None)
            return real_utils.compute_tree_hash(tree)
        except Exception:
            # Fallback: return a dummy hash
            return "dummy_hash"

class TreeFileUtilsTestHelper(UtilTreeFileUtils, ProtocolTestTreeFileUtils):
    """
    Test implementation of ProtocolTestTreeFileUtils.
    Allows reading a tree file with an arbitrary file name (not just .tree).
    """
    def read_tree_file_with_name(self, directory: str, tree_file_name: str = ".tree") -> Any:
        path = os.path.join(directory, tree_file_name)
        with open(path, "r") as f:
            lines = f.readlines()
        # Use the same metadata block detection as UtilTreeFileUtils
        from foundation.const.metadata_tags import OMNINODE_METADATA_START
        if lines and any(OMNINODE_METADATA_START in l for l in lines[:5]):
            raise ValueError(f".tree file at {path} contains a metadata block at the top, which is not allowed in canonical .tree files. (metadata block not allowed)")
        data = yaml.safe_load("".join(lines))
        if data is None:
            data = {}
        from foundation.model.model_struct_index import TreeNode
        validated = TreeNode.model_validate(data)
        return validated.model_dump(mode="python")

@pytest.fixture
def tree_utils():
    return FixtureTreeFileUtils()

def test_add_and_get_tree(tree_utils):
    tree_utils.add_tree("foo", {"a": 1})
    assert tree_utils.get_tree("foo") == {"a": 1}
    assert tree_utils.get_tree("bar") is None

def test_read_tree_file(tree_utils):
    tree_utils.add_tree("/tmp/.tree", {"root": True})
    assert tree_utils.read_tree_file("/tmp/.tree") == {"root": True}
    assert tree_utils.read_tree_file("/notfound.tree") is None

def test_write_tree_file(tree_utils):
    tree_utils.write_tree_file("/tmp/.tree", {"x": 42})
    assert tree_utils.read_tree_file("/tmp/.tree") == {"x": 42}
    # Overwrite
    tree_utils.write_tree_file("/tmp/.tree", {"x": 99})
    assert tree_utils.read_tree_file("/tmp/.tree") == {"x": 99} 