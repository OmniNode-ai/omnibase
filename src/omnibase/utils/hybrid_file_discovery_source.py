"""
Hybrid file discovery source for stamping/validation tools.
Combines filesystem and .tree-based discovery, with drift detection and enforcement.
Implements ProtocolFileDiscoverySource.
"""

from pathlib import Path
from typing import List, Optional, Set

from omnibase.model.model_tree_sync_result import (
    TreeSyncResultModel,
    TreeSyncStatusEnum,
)
from omnibase.protocol.protocol_file_discovery_source import ProtocolFileDiscoverySource
from omnibase.utils.directory_traverser import DirectoryTraverser
from omnibase.utils.tree_file_discovery_source import TreeFileDiscoverySource


class HybridFileDiscoverySource(ProtocolFileDiscoverySource):
    """
    Hybrid file discovery source: uses filesystem, but cross-checks with .tree if present.
    Warns or errors on drift depending on strict_mode.
    """

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.fs_source = DirectoryTraverser()
        self.tree_source = TreeFileDiscoverySource()

    def discover_files(
        self,
        directory: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        ignore_file: Optional[Path] = None,
    ) -> Set[Path]:
        """
        Discover files using filesystem, but cross-check with .tree if present.
        Warn or error on drift depending on strict_mode.
        """
        tree_file = directory / ".tree"
        files = self.fs_source.find_files(
            directory, include_patterns, exclude_patterns, True, ignore_file
        )
        if tree_file.exists():
            sync_result = self.validate_tree_sync(directory, tree_file)
            if sync_result.status == TreeSyncStatusEnum.DRIFT:
                msg = "; ".join(m.summary for m in sync_result.messages)
                if self.strict_mode:
                    raise RuntimeError(
                        f"Drift detected between filesystem and .tree: {msg}"
                    )
                else:
                    print(
                        f"[WARNING] Drift detected between filesystem and .tree: {msg}"
                    )
            # Optionally, filter to only files in .tree if strict_mode
            if self.strict_mode:
                files = files & self.tree_source.get_canonical_files_from_tree(
                    tree_file
                )
        return files

    def validate_tree_sync(
        self,
        directory: Path,
        tree_file: Path,
    ) -> TreeSyncResultModel:
        """
        Validate that the .tree file and filesystem are in sync.
        """
        return self.tree_source.validate_tree_sync(directory, tree_file)

    def get_canonical_files_from_tree(self, tree_file: Path) -> Set[Path]:
        """
        Get canonical files from .tree file.
        """
        return self.tree_source.get_canonical_files_from_tree(tree_file)
