# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "model_directory_tree"
# namespace: "omninode.model.directory_tree"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00Z"
# last_modified_at: "2025-05-07T12:00:00Z"
# entrypoint: "model_directory_tree.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["ModelProtocol"]
# base_class: ["BaseModel"]
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""Models for directory tree validation."""

from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class DirectoryPattern(BaseModel):
    """Pattern for matching directory names."""
    pattern: str
    description: Optional[str] = None

    def serialize(self) -> dict:
        return self.model_dump(by_alias=True, exclude_unset=True)


class ValidationRule(BaseModel):
    """Rule for validating files/directories."""
    name: str
    pattern: str
    required: bool = False
    description: Optional[str] = None
    required_path: Optional[str] = None

    def serialize(self) -> dict:
        return self.model_dump(by_alias=True, exclude_unset=True)


class CanonicalPath(BaseModel):
    """Canonical path definition."""
    path: str
    allowed_files: List[DirectoryPattern]
    allowed_dirs: List[DirectoryPattern]

    def serialize(self) -> dict:
        return {
            "path": self.path,
            "allowed_files": [f.serialize() for f in self.allowed_files],
            "allowed_dirs": [d.serialize() for d in self.allowed_dirs],
        }


class DirectoryTreeRules(BaseModel):
    """Rules for directory tree validation."""
    allow_flexible: List[str]
    deny_unlisted: bool = True

    def serialize(self) -> dict:
        return self.model_dump(by_alias=True, exclude_unset=True)


class DirectoryTreeStructure(BaseModel):
    """Structure of a directory tree."""
    path: str
    children: Dict[str, Any]

    def serialize(self) -> dict:
        # Recursively serialize children if they are DirectoryTreeStructure
        return {
            "path": self.path,
            "children": {
                k: v.serialize() if hasattr(v, 'serialize') else v
                for k, v in self.children.items()
            }
        }

# === Legacy Model: DirectoryTreeTemplate (DEPRECATED, for migration only) ===
# TODO: Remove after migration to TreeNode is complete.
class DirectoryTreeTemplate(BaseModel):
    """Template for directory tree validation (legacy, DEPRECATED)."""
    root: str
    canonical_paths: List[CanonicalPath]
    validation_rules: List[ValidationRule]
    rules: DirectoryTreeRules

    def serialize(self) -> dict:
        return self.model_dump(by_alias=True, exclude_unset=True) 