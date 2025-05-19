# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 43d56eff-81e3-4d83-8662-cbe79df2f72b
# name: model_enum_ignore_pattern_source.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:03.979432
# last_modified_at: 2025-05-19T16:20:03.979433
# description: Stamped Python file: model_enum_ignore_pattern_source.py
# state_contract: none
# lifecycle: active
# hash: c0663670140290a3d7f334498ebdef11555aa59196b766652d7c6ba0d91f4ffc
# entrypoint: {'type': 'python', 'target': 'model_enum_ignore_pattern_source.py'}
# namespace: onex.stamped.model_enum_ignore_pattern_source.py
# meta_type: tool
# === /OmniNode:Metadata ===

"""
Enums for file traversal and ignore pattern handling.
"""

from enum import Enum


class IgnorePatternSourceEnum(str, Enum):
    """
    Canonical sources for ignore patterns when traversing directories.

    This enum defines the possible sources for ignore patterns when
    filtering files during directory traversal operations.
    """

    FILE = "file"  # Patterns from an ignore file (e.g., .stamperignore)
    DIRECTORY = "directory"  # Default directory patterns to ignore (e.g., .git)
    USER = "user"  # User-provided patterns via CLI or API
    DEFAULT = "default"  # Built-in default patterns from the application
    NONE = "none"  # No ignore patterns (process all files)


class TraversalModeEnum(str, Enum):
    """
    Canonical modes for directory traversal.

    This enum defines the possible modes for traversing directories when
    processing files.
    """

    RECURSIVE = "recursive"  # Recursively traverse all subdirectories
    FLAT = "flat"  # Only process files in the specified directory
    SHALLOW = "shallow"  # Process files in the specified directory and immediate subdirectories
    CUSTOM = "custom"  # Custom traversal based on specific rules
