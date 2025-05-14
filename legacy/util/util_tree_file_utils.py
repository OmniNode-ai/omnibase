import yaml
from typing import Any
from pydantic import ValidationError
from foundation.protocol.protocol_tree_file_utils import ProtocolTreeFileUtils
from foundation.model.model_struct_index import TreeNode
from foundation.model.model_metadata import MetadataBlockModel
from foundation.util.util_hash_utils import UtilHashUtils
from foundation.util.util_metadata_block_extractor_registry import get_extractor
import copy
import os
import structlog
from foundation.const.metadata_tags import OMNINODE_METADATA_START, OMNINODE_METADATA_END
from pathlib import Path

class UtilTreeFileUtils(ProtocolTreeFileUtils):
    """
    Real implementation of ProtocolTreeFileUtils for reading and writing .tree files on disk.
    Enforces schema validation using the TreeNode Pydantic model on both read and write.
    Implements hash-based update logic for .tree files.
    Now uses YAML frontmatter metadata block at the top of the file.
    """
    def __init__(self, logger):
        if logger is None:
            raise ValueError("UtilTreeFileUtils requires a logger to be injected via DI.")
        self.logger = logger

    def compute_tree_hash(self, tree: Any) -> str:
        """
        Compute a canonical SHA-256 hash of the .tree structure, excluding the 'tree_hash' field in metadata.
        Args:
            tree: The tree structure (dict or TreeNode) to hash.
        Returns:
            str: The SHA-256 hash as a hex string.
        """
        logger = self.logger
        logger.debug("Computing tree hash", input_type=type(tree).__name__, input_repr=repr(tree)[:500])
        try:
            # If tree is a Pydantic model, convert to dict
            if hasattr(tree, 'model_dump'):
                tree_copy = tree.model_dump()
            elif hasattr(tree, 'serialize'):
                tree_copy = tree.serialize()
            else:
                tree_copy = tree
            logger.debug("Tree to be serialized", tree_type=type(tree_copy).__name__, tree_repr=repr(tree_copy)[:500])
            # Deep copy and remove 'tree_hash' from metadata if present
            tree_copy = copy.deepcopy(tree_copy)
            if isinstance(tree_copy, dict):
                meta = tree_copy.get("metadata", {})
                if meta is None:
                    meta = {}
                if "tree_hash" in meta:
                    del meta["tree_hash"]
            elif hasattr(tree_copy, 'metadata') and tree_copy.metadata and hasattr(tree_copy.metadata, 'pop'):
                tree_copy.metadata.pop("tree_hash", None)
            # Use yaml.safe_dump for canonical serialization
            tree_str = yaml.safe_dump(tree_copy, sort_keys=True)
            logger.debug("YAML serialization succeeded", tree_str=tree_str[:500])
        except Exception as e:
            logger.error("YAML serialization failed", error=str(e), tree_type=type(tree).__name__, tree_repr=repr(tree)[:500])
            raise
        return UtilHashUtils.compute_hash(tree_str)

    def is_tree_file_up_to_date(self, path: str, tree: Any) -> bool:
        """
        Check if the .tree file at 'path' is up-to-date with the given tree structure (by comparing hashes).
        Args:
            path: Path to the .tree file.
            tree: The tree structure to compare.
        Returns:
            bool: True if up-to-date, False otherwise.
        """
        if not os.path.exists(path):
            return False
        with open(path, "r") as f:
            lines = f.readlines()
        extractor = get_extractor('tree')
        block_str = extractor.extract_block(lines) if extractor else None
        file_hash = None
        if block_str:
            metadata = yaml.safe_load(block_str)
            file_hash = metadata.get("tree_hash")
        current_hash = self.compute_tree_hash(tree)
        return file_hash == current_hash

    def read_tree_file(self, path: str) -> TreeNode:
        """Read a .tree YAML file from disk and validate against the TreeNode schema. Reject files with a metadata block at the top."""
        with open(path, "r") as f:
            lines = f.readlines()
        # Check for metadata block at the top
        if lines and any(OMNINODE_METADATA_START in l for l in lines[:5]):
            print(f"DEBUG: Metadata block detected in {path}, raising error.")
            raise ValueError(f".tree file at {path} contains a metadata block at the top, which is not allowed in canonical .tree files. (metadata block not allowed)")
        data = yaml.safe_load("".join(lines))
        if data is None:
            data = {}
        validated = TreeNode.model_validate(data)
        return validated

    def write_tree_file(self, path: str, tree: Any, force: bool = False) -> None:
        """
        Validate tree data against the TreeNode schema before writing to disk.
        Write as pure YAML (no metadata block at the top).
        Only write if the file content differs or force=True.
        """
        try:
            validated = TreeNode.model_validate(tree)
            tree_dict = validated.model_dump(mode="python")
            # Remove metadata if present
            tree_dict.pop("metadata", None)
            content = yaml.safe_dump(tree_dict, sort_keys=True)
            # Only write if content differs or force
            if not force and os.path.exists(path):
                with open(path, "r") as f:
                    existing = f.read()
                if existing == content:
                    return  # Up-to-date, skip write
            with open(path, "w") as f:
                f.write(content)
        except ValidationError as e:
            raise ValueError(f"Attempted to write invalid .tree data to {path}: {e}")

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

    def directory_to_tree_node(self, root_dir: str, max_depth: int = -1, include: str = None, exclude: str = None, follow_symlinks: bool = False, flat: bool = False, with_metadata: bool = False, verbose: bool = False) -> TreeNode:
        """
        Recursively walk a directory and return a TreeNode Pydantic model representing the structure.
        Args:
            root_dir: Root directory path to scan.
            max_depth, include, exclude, follow_symlinks, flat, with_metadata, verbose: Passed to StructIndex.build_tree.
        Returns:
            TreeNode representing the structure.
        """
        from foundation.script.tool.struct.struct_index import StructIndex
        indexer = StructIndex(logger=self.logger)
        root_path = Path(root_dir) if isinstance(root_dir, str) else root_dir
        return indexer.build_tree(
            directory=root_path,
            max_depth=max_depth,
            include=include,
            exclude=exclude,
            follow_symlinks=follow_symlinks,
            flat=flat,
            with_metadata=with_metadata,
            verbose=verbose
        ) 