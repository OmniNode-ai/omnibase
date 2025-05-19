# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: ac223db5-189a-4287-b066-849b9b4e62f2
# name: protocol_file_discovery_source.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:55.586015
# last_modified_at: 2025-05-19T16:19:55.586016
# description: Stamped Python file: protocol_file_discovery_source.py
# state_contract: none
# lifecycle: active
# hash: 1ee80e68e7e7636e0218e07f6cf1ecd1d94e064f98b602a51f298185b946b20d
# entrypoint: {'type': 'python', 'target': 'protocol_file_discovery_source.py'}
# namespace: onex.stamped.protocol_file_discovery_source.py
# meta_type: tool
# === /OmniNode:Metadata ===

"""
Protocol for file discovery sources (filesystem, .tree, hybrid, etc.).
Defines a standardized interface for discovering and validating files for stamping/validation.
"""

from pathlib import Path
from typing import Optional, Protocol, Set

from omnibase.model.model_tree_sync_result import TreeSyncResultModel


class ProtocolFileDiscoverySource(Protocol):
    """
    Protocol for file discovery sources.
    Implementations may use the filesystem, .tree files, or other sources.
    """

    def discover_files(
        self,
        directory: Path,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
        ignore_file: Optional[Path] = None,
    ) -> Set[Path]:
        """
        Discover eligible files for stamping/validation in the given directory.
        Args:
            directory: Root directory to search
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude
            ignore_file: Optional ignore file (e.g., .stamperignore)
        Returns:
            Set of Path objects for eligible files
        """
        ...

    def validate_tree_sync(
        self,
        directory: Path,
        tree_file: Path,
    ) -> TreeSyncResultModel:
        """
        Validate that the .tree file and filesystem are in sync.
        Args:
            directory: Root directory
            tree_file: Path to .tree file
        Returns:
            TreeSyncResultModel with drift info and status
        """
        ...

    def get_canonical_files_from_tree(
        self,
        tree_file: Path,
    ) -> Set[Path]:
        """
        Get the set of canonical files listed in a .tree file.
        Args:
            tree_file: Path to .tree file
        Returns:
            Set of Path objects listed in .tree
        """
        ...
