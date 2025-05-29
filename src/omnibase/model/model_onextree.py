# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.699796'
# description: Stamped by PythonHandler
# entrypoint: python://model_onextree.py
# hash: 3a600c8f3dc2702a10244d5729a6a4748361ff05f1ec4080ab5389ea06fdac98
# last_modified_at: '2025-05-29T11:50:11.032405+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_onextree.py
# namespace: omnibase.model_onextree
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: dac5f0f8-b96b-49ff-ad76-3b0c32101caf
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Pydantic models for .onextree file structure.

This module provides typed models for parsing and validating .onextree files,
replacing the previous Dict[str, Any] approach with proper type safety.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Generator, List, Optional, Union, cast

from pydantic import BaseModel, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError


class OnextreeNodeTypeEnum(Enum):
    """Types of nodes in the .onextree structure."""

    FILE = "file"
    DIRECTORY = "directory"


class OnextreeNode(BaseModel):
    """
    A node in the .onextree structure.

    Represents either a file or directory with optional children.
    """

    name: str = Field(..., description="Name of the file or directory")
    type: OnextreeNodeTypeEnum = Field(..., description="Type of the node")
    children: Optional[List["OnextreeNode"]] = Field(
        default=None, description="Child nodes (only for directories)"
    )

    @field_validator("children")
    @classmethod
    def validate_children(
        cls, v: Optional[List["OnextreeNode"]], info: Any
    ) -> Optional[List["OnextreeNode"]]:
        """Validate that only directories can have children."""
        if info.data:
            node_type = info.data.get("type")
            if node_type == OnextreeNodeTypeEnum.FILE and v is not None:
                raise OnexError(
                    "Files cannot have children", CoreErrorCode.INVALID_PARAMETER
                )
            if node_type == OnextreeNodeTypeEnum.DIRECTORY and v is None:
                # Directories can have empty children list
                return []
        return v

    def is_file(self) -> bool:
        """Check if this node is a file."""
        return self.type == OnextreeNodeTypeEnum.FILE

    def is_directory(self) -> bool:
        """Check if this node is a directory."""
        return self.type == OnextreeNodeTypeEnum.DIRECTORY

    def find_child(self, name: str) -> Optional["OnextreeNode"]:
        """Find a direct child by name."""
        if not self.children:
            return None
        return next((child for child in self.children if child.name == name), None)

    def find_file(self, filename: str) -> Optional["OnextreeNode"]:
        """Find a file in direct children."""
        if not self.children:
            return None
        return next(
            (
                child
                for child in self.children
                if child.is_file() and child.name == filename
            ),
            None,
        )

    def find_directory(self, dirname: str) -> Optional["OnextreeNode"]:
        """Find a directory in direct children."""
        if not self.children:
            return None
        return next(
            (
                child
                for child in self.children
                if child.is_directory() and child.name == dirname
            ),
            None,
        )

    def get_path(self, root_path: Optional[Path] = None) -> Path:
        """Get the full path of this node."""
        if root_path:
            return root_path / self.name
        return Path(self.name)

    def walk(
        self, path_prefix: Optional[Path] = None
    ) -> "Generator[tuple[Path, OnextreeNode], None, None]":
        """
        Walk the tree yielding (path, node) tuples.

        Args:
            path_prefix: Prefix to add to paths

        Yields:
            Tuple of (full_path, node)
        """
        current_path = path_prefix / self.name if path_prefix else Path(self.name)
        yield current_path, self

        if self.children:
            for child in self.children:
                yield from child.walk(current_path)


class OnextreeRoot(BaseModel):
    """
    Root model for .onextree files.

    This represents the complete .onextree structure starting from the root directory.
    """

    name: str = Field(..., description="Name of the root directory")
    type: OnextreeNodeTypeEnum = Field(
        default=OnextreeNodeTypeEnum.DIRECTORY,
        description="Type of the root (should always be directory)",
    )
    children: List[OnextreeNode] = Field(
        default_factory=list, description="Child nodes of the root directory"
    )

    @field_validator("type")
    @classmethod
    def validate_root_type(cls, v: OnextreeNodeTypeEnum) -> OnextreeNodeTypeEnum:
        """Validate that root is always a directory."""
        if v != OnextreeNodeTypeEnum.DIRECTORY:
            raise OnexError(
                "Root node must be a directory", CoreErrorCode.INVALID_PARAMETER
            )
        return v

    def is_file(self) -> bool:
        """Check if this node is a file."""
        return self.type == OnextreeNodeTypeEnum.FILE

    def is_directory(self) -> bool:
        """Check if this node is a directory."""
        return self.type == OnextreeNodeTypeEnum.DIRECTORY

    def find_artifact_directories(self) -> List[tuple[Path, OnextreeNode]]:
        """
        Find all artifact directories (nodes, cli_tools, etc.) in the tree.

        Returns:
            List of (path, node) tuples for artifact directories
        """
        artifact_dirs = []
        artifact_types = {
            "nodes",
            "cli_tools",
            "runtimes",
            "adapters",
            "contracts",
            "packages",
        }

        for path, node in self.walk():
            if node.is_directory() and node.name in artifact_types:
                artifact_dirs.append((path, node))

        return artifact_dirs

    def find_versioned_artifacts(self) -> List[tuple[str, str, str, OnextreeNode]]:
        """
        Find all versioned artifacts in the tree.

        Returns:
            List of (artifact_type, artifact_name, version, node) tuples
        """
        artifacts = []

        for path, node in self.walk():
            parts = path.parts

            # Look for patterns like: omnibase/nodes/node_name/v1_0_0
            if len(parts) >= 4:
                for i in range(len(parts) - 2):
                    type_part = parts[i]

                    if type_part in {
                        "nodes",
                        "cli_tools",
                        "runtimes",
                        "adapters",
                        "contracts",
                        "packages",
                    }:
                        if i + 2 < len(parts):
                            name_part = parts[i + 1]
                            version_part = parts[i + 2]

                            if version_part.startswith("v") and node.is_directory():
                                artifacts.append(
                                    (type_part, name_part, version_part, node)
                                )

        return artifacts

    def find_metadata_files(self) -> List[tuple[Path, OnextreeNode]]:
        """
        Find all metadata files (node.onex.yaml, cli_tool.yaml, etc.) in the tree.

        Returns:
            List of (path, node) tuples for metadata files
        """
        metadata_files = []
        metadata_patterns = {
            "node.onex.yaml",
            "cli_tool.yaml",
            "runtime.yaml",
            "adapter.yaml",
            "contract.yaml",
            "package.yaml",
        }

        for path, node in self.walk():
            if node.is_file() and node.name in metadata_patterns:
                metadata_files.append((path, node))

        return metadata_files

    def walk(self) -> "Generator[tuple[Path, OnextreeNode], None, None]":
        """
        Walk the entire tree yielding (path, node) tuples.

        Yields:
            Tuple of (full_path, node)
        """
        yield Path(self.name), cast(OnextreeNode, self)

        for child in self.children:
            yield from child.walk(Path(self.name))

    @classmethod
    def from_dict(cls, data: dict) -> "OnextreeRoot":
        """
        Create an OnextreeRoot from a dictionary (e.g., from YAML).

        Args:
            data: Dictionary representation of the .onextree

        Returns:
            OnextreeRoot instance
        """
        return cls.model_validate(data)

    @classmethod
    def from_yaml_file(cls, file_path: Union[str, Path]) -> "OnextreeRoot":
        """
        Load an OnextreeRoot from a YAML file.

        Args:
            file_path: Path to the .onextree file

        Returns:
            OnextreeRoot instance
        """
        import yaml

        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)


# Enable forward references for recursive model
OnextreeNode.model_rebuild()
