# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node_metadata_loader.py
# version: 1.0.0
# uuid: d9564116-0848-41ce-8fb5-4988d546143d
# author: OmniNode Team
# created_at: 2025-05-26T16:58:32.064188
# last_modified_at: 2025-05-27T09:37:09.031926
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d38004be5bf968d1c4b5c4ce2eea6bda615cceef4afd0ee44d94ac153790db50
# entrypoint: python@node_metadata_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.node_metadata_loader
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Core utility for loading node metadata from node.onex.yaml files.
Uses existing SchemaLoader infrastructure to prevent drift between constants and actual metadata.
"""

from pathlib import Path
from typing import Optional

from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.schemas.loader import SchemaLoader


class NodeMetadataLoader:
    """Loads node metadata from node.onex.yaml files using existing infrastructure."""

    def __init__(
        self,
        node_directory: Optional[Path] = None,
        schema_loader: Optional[SchemaLoader] = None,
    ):
        """
        Initialize the metadata loader.

        Args:
            node_directory: Path to the node directory. If None, auto-detects from caller's location.
            schema_loader: Optional SchemaLoader instance. If None, creates a new one.
        """
        self.node_directory = node_directory
        self._metadata: Optional[NodeMetadataBlock] = None
        self._schema_loader = schema_loader or SchemaLoader()

    def _resolve_node_directory(self) -> Path:
        """Resolve the node directory, auto-detecting if not provided."""
        if self.node_directory is not None:
            return self.node_directory

        # Auto-detect from caller's location
        # This is a fallback - callers should provide explicit paths
        import inspect

        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            caller_file = frame.f_back.f_back.f_globals.get("__file__")
            if caller_file:
                caller_path = Path(caller_file)
                # Look for node.onex.yaml in current directory or parent directories
                current = caller_path.parent
                for _ in range(5):  # Limit search depth
                    if (current / "node.onex.yaml").exists():
                        return current
                    current = current.parent

        from omnibase.core.error_codes import CoreErrorCode, OnexError

        raise OnexError(
            "Could not auto-detect node directory. Please provide explicit node_directory parameter.",
            CoreErrorCode.INVALID_PARAMETER,
        )

    @property
    def metadata_file(self) -> Path:
        """Get the path to the node.onex.yaml file."""
        return self._resolve_node_directory() / "node.onex.yaml"

    @property
    def metadata(self) -> NodeMetadataBlock:
        """Get the node metadata, loading it if not already cached."""
        if self._metadata is None:
            self._metadata = self._schema_loader.load_onex_yaml(self.metadata_file)
        return self._metadata

    def reload(self) -> NodeMetadataBlock:
        """Force reload the metadata from disk."""
        self._metadata = None
        return self.metadata

    @property
    def node_name(self) -> str:
        """Get the node name from metadata."""
        return self.metadata.name

    @property
    def node_version(self) -> str:
        """Get the node version from metadata."""
        return self.metadata.version

    @property
    def node_description(self) -> str:
        """Get the node description from metadata."""
        return self.metadata.description

    @property
    def node_author(self) -> str:
        """Get the node author from metadata."""
        return self.metadata.author


def load_node_metadata(node_directory: Path) -> NodeMetadataBlock:
    """
    Convenience function to load node metadata from a directory.

    Args:
        node_directory: Path to the directory containing node.onex.yaml

    Returns:
        NodeMetadataBlock instance
    """
    loader = NodeMetadataLoader(node_directory)
    return loader.metadata


def get_node_name(node_directory: Path) -> str:
    """
    Convenience function to get just the node name.

    Args:
        node_directory: Path to the directory containing node.onex.yaml

    Returns:
        Node name string
    """
    return load_node_metadata(node_directory).name
