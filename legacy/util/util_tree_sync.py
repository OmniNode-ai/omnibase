# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# name: "util_tree_sync"
# namespace: "foundation.util"
# meta_type: "util"
# version: "0.1.0"
# owner: "foundation-team"
# entrypoint: "util_tree_sync.py"
# === /OmniNode:Tool_Metadata ===

import os
from pathlib import Path
from typing import List, Any
from foundation.model.model_struct_index import TreeNode
from foundation.protocol.protocol_tree_file_utils import ProtocolTreeFileUtils
import yaml


def directory_to_tree_template(path: str) -> TreeNode:
    """
    Recursively walk a directory and return a TreeNode representing the structure.
    Args:
        path: Root directory path to scan.
    Returns:
        TreeNode representing the structure.
    """
    path = Path(path)
    def build_tree(node_path: Path) -> TreeNode:
        children = []
        if node_path.is_dir():
            for entry in sorted(node_path.iterdir()):
                children.append(build_tree(entry))
            return TreeNode(
                name=node_path.name,
                type="directory",
                children=children,
                metadata=None
            )
        else:
            return TreeNode(
                name=node_path.name,
                type="file",
                children=None,
                metadata=None
            )
    return build_tree(path)


def tree_template_to_directory(template: TreeNode, path: str) -> None:
    """
    Given a TreeNode, create the directory structure at the given path.
    Args:
        template: TreeNode model.
        path: Root directory to create structure in.
    """
    path = Path(path)
    for canonical in template.canonical_paths:
        dir_path = path / canonical.path
        dir_path.mkdir(parents=True, exist_ok=True)
        for dpat in canonical.allowed_dirs:
            (dir_path / dpat.pattern).mkdir(exist_ok=True)
        for fpat in canonical.allowed_files:
            # Only create a placeholder file for the pattern if it's a specific file, not a wildcard
            if not ("*" in fpat.pattern or "?" in fpat.pattern):
                (dir_path / fpat.pattern).touch(exist_ok=True)


class UtilTreeFileUtils(ProtocolTreeFileUtils):
    """
    Real implementation of ProtocolTreeFileUtils for file system operations.
    """
    def read_tree_file(self, path: str) -> Any:
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def write_tree_file(self, path: str, tree: Any) -> None:
        with open(path, "w") as f:
            yaml.safe_dump(tree, f)

    def add_tree(self, name: str, tree: Any) -> None:
        # Not applicable for real file system; no-op or could raise NotImplementedError
        pass

    def get_tree(self, name: str) -> Any:
        # Not applicable for real file system; no-op or could raise NotImplementedError
        return None 