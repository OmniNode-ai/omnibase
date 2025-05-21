# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_file_discovery_source.py
# version: 1.0.0
# uuid: 96d84162-9e4f-4bce-8aec-22d63cb8bc67
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167004
# last_modified_at: 2025-05-21T16:42:46.060923
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 4eed2db571c589ed1c76cfe44b0b4baf3852a6b7471accb25f4d86eb4adcd8fa
# entrypoint: {'type': 'python', 'target': 'protocol_file_discovery_source.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_file_discovery_source
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
