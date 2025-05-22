# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_enum_ignore_pattern_source.py
# version: 1.0.0
# uuid: 500ad575-ce0d-4a4e-8335-12594e3c2c2e
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165128
# last_modified_at: 2025-05-21T16:42:46.048020
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: c09214342293dd31987d16d17103fbf7f9fb5ebb7378812dfbe933acc3c100a7
# entrypoint: python@model_enum_ignore_pattern_source.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_enum_ignore_pattern_source
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
